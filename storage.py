from storage.models import Storage ,Equipments
from django.contrib import auth
from django.core.exceptions import ObjectDoesNotExist
from django.template.context_processors import csrf
from django.http import JsonResponse
from loginsys.models import CompanyReg
from django.shortcuts import render_to_response, redirect, HttpResponse
from storage.models import *
from django.contrib.auth.models import User
from billing.models import CodeName, UserPlan
from storage.forms import *
import simplejson as json
from chat.views import new_system_message
from company.views import top_four_elements

def storage(request):
    user = auth.get_user(request)
    args = {}
    args.update(csrf(request))
    args['user'] = user
    args['username'] = user.username
    args['company'] = CompanyReg.objects.get(user=user.profile.company_id)
    list_perms = []
    [list_perms.append(i) for i in user.get_all_permissions()]
    args['user_perms'] = list_perms
    if request.user.has_perm('storage.change_storage') or request.user.has_perm('storage.add_storage') or request.user.has_perm('storage.delete_storage') or request.user.has_perm('storage.add_equipments'):
        workers = User.objects.all().filter(profile__company_id=user.profile.company_id)
        storage_items = Storage.objects.filter(company_id=user.profile.company_id)
        args['storage_items'] = storage_items
        args['top_four'] = top_four_elements(request)
        args['workers'] = workers
        return render_to_response('storage.html', args)
    else:
        args['access_denied'] = True
        return render_to_response('storage.html', args)


def storage_items_json(request):
    if request.user.has_perm('storage.add_storage') or request.user.has_perm('storage.change_storage')or request.user.has_perm('storage.delete_storage') or request.user.has_perm('storage.add_equipments'):
        user_plan = UserPlan.objects.get(user=request.user.profile.company_id)
        code_name = CodeName.objects.get(name='storage')
        try:
            storage_count = user_plan.plan.options.get(code_name=code_name.id).amount
        except ObjectDoesNotExist:
            storage_count = 0
        finally:
            request_type = request.GET.get('for', '')
            item_id = request.GET.get('id', '')
            if item_id != '':
                if request_type != 'inventory':
                    try:
                        item = Storage.objects.filter(company_id=request.user.profile.company_id).get(id=item_id)
                        result = {
                            'error': False,
                            'item': item.as_dict()
                        }
                        if storage_count == 0:
                            result = {
                                'error': True,
                                'message': 'Sorry. In you plan don\'t have this option.'
                            }
                        return JsonResponse(result, safe=False)
                    except ObjectDoesNotExist:
                        result = {
                            'error': True,
                            'message': 'Item dosn\'t exist'
                        }
                        return JsonResponse(result, safe=False)
                else:
                    try:
                        item = Equipments.objects.get(id=item_id)
                    except ObjectDoesNotExist:
                        result = {
                            'error': True,
                            'message': 'Item dosn\'t exist'
                        }
                        return JsonResponse(result, safe=False)
                    result = {
                        'error': False,
                        'item': item.as_dict()
                    }
                    if storage_count == 0:
                        result = {
                            'error': True,
                            'message': 'Sorry. In you plan don\'t have this option.'
                        }
                    return JsonResponse(result, safe=False)
            items_list = Storage.objects.filter(company_id=request.user.profile.company_id)
            if storage_count >= 0:
                items_list = items_list.order_by('id')[:storage_count]
            return_list = []
            if request_type == 'table':
                for i in items_list:
                    return_list.append(i.as_dict())
                result_dict = {
                    'draw': 1,
                    'recordsTotal': len(items_list),
                    'recordsFiltered': len(items_list),
                    'data': return_list
                }
                return JsonResponse(result_dict, safe=False)
            elif request_type == 'select':
                q = request.GET.get('q', '')
                if q != '':
                    items_name = Storage.objects.filter(company_id=request.user.profile.company_id).filter(item_name__icontains=q)
                    if storage_count >= 0:
                        items_name = items_name.order_by('id')[:storage_count]
                    [return_list.append({'id': i.id, 'text': i.item_name}) for i in items_name]
                    return JsonResponse(return_list, safe=False)
                else:
                    [return_list.append({'id': i.id, 'text': i.item_name}) for i in items_list]
                    return JsonResponse(return_list, safe=False)
            else:
                JsonResponse('Unknown value for variable \'for\'.', safe=False, status=500)
    else:
        return JsonResponse('Sorry. You don\'t have permissions for this action.', safe=False, status=403)


def new_storage_item(request):
    if request.user.has_perm('storage.add_storage'):
        if request.POST:
            user_plan = UserPlan.objects.get(user=request.user.profile.company_id)
            code_name = CodeName.objects.get(name='storage')
            try:
                storage_count = user_plan.plan.options.get(code_name=code_name.id).amount
            except ObjectDoesNotExist:
                return JsonResponse({
                    'error': True,
                    'message': 'Sorry. In you plan don\'t have this option.'
                }, safe=False)
            else:
                count_stor = Storage.objects.filter(company_id=request.user.profile.company_id).count()
                if count_stor < storage_count or storage_count == -1:
                    item_name = request.POST.get('item_name', '')
                    amount_str = request.POST.get('amount', '')
                    if amount_str != '':
                        amount = float(amount_str)
                    else:
                        amount = 0
                    sell_price_str = request.POST.get('sell_price', '')
                    if sell_price_str != '':
                        sell_price = float(sell_price_str)
                    else:
                        sell_price = 0
                    company_id = request.user.profile.company_id
                    st_item = Storage.objects.create(
                        item_name=item_name,
                        amount=amount,
                        sell_price=sell_price,
                        company_id=company_id
                    )
                    StorageHistory.objects.create(
                        user=request.user,
                        message='Created new item: <b>' + st_item.item_name + '</b>, amount = <b>' + str(st_item.amount) + '</b>, sell price = <b>' + str(st_item.sell_price) + '</b>',
                        company_id=request.user.profile.company_id
                    )
                    name_user = request.user.first_name + ' ' + request.user.last_name
                    if len(name_user) < 3:
                        name_user = request.user.profile.position
                    permissions = tuple(['add_storage'])
                    chat_message = '<b>'+name_user+'</b> create storage item: '+item_name
                    new_system_message(request, chat_message, permissions)
                    return JsonResponse({'error': False, 'id': st_item.id}, safe=False)
                else:
                    return JsonResponse({
                        'error': True,
                        'message': 'Sorry. You don\'t have longer create storage item.'
                    }, safe=False)
        else:
            return JsonResponse({
                'error': True,
                'message': 'You try do unknown action.'
            }, safe=False, status=404)
    else:
        return JsonResponse({
            'error': True,
            'message': 'Sorry. You don\'t have permissions for this action.'
        }, safe=False, status=403)


def edit_storage_item(request):
    if request.user.has_perm('storage.change_storage'):
        item_id = request.POST.get('item-id', '')
        try:
            storage_item = Storage.objects.filter(company_id=request.user.profile.company_id).get(id=int(item_id))
        except ObjectDoesNotExist:
            return JsonResponse({
                'error': True,
                'message': 'Storage item does not exist'
            }, safe=False)
        amount = request.POST.get('amount', '')
        history_message = 'Change item: <b>' + storage_item.item_name + '</b>'
        if amount != '':
            storage_item.amount = float(amount)
            history_message += ', amount = <b>' + str(storage_item.amount) + '</b>'
        sell_price = request.POST.get('sell-price', '')
        if sell_price != '':
            storage_item.sell_price = float(sell_price)
            history_message += ', sell_price = <b>' + str(storage_item.sell_price) + '</b>'
        item_name = request.POST.get('item-name', '')
        if item_name != '':
            storage_item.item_name = item_name
            history_message += ', item name to <b>' + storage_item.item_name + '</b>'
        storage_item.save()
        StorageHistory.objects.create(
            user=request.user,
            message=history_message + ' ' + request.POST.get('comment', ''),
            company_id=request.user.profile.company_id
        )
        name_user = request.user.first_name + ' ' + request.user.last_name
        if len(name_user) < 3:
            name_user = request.user.profile.position
        permissions = tuple(['change_storage'])
        chat_message = '<b>'+name_user+'</b> change storage item: '+storage_item.item_name
        new_system_message(request, chat_message, permissions)
        return JsonResponse({
            'error': False,
            'message': 'OK'
        }, safe=False)
    else:
        return JsonResponse({
            'error': True,
            'message': 'You don\'t have permissons for this action.'
        }, safe=False)


def add_amount(request):
    if request.user.has_perm('storage.change_storage'):
        if request.POST:
            item_id = int(request.POST.get('storage_item_id'))
            amount = float(request.POST.get('amount'))
            storage_item = Storage.objects.get(id=item_id)
            old_amount = storage_item.amount
            storage_item.amount = old_amount + amount
            storage_item.save()
            StorageHistory.objects.create(
                user=request.user,
                company_id=request.user.profile.company_id,
                message='Add item <b>' + storage_item.item_name + '</b> amount: previous value <b>' + str(old_amount) + '</b>, amount <b>' + str(amount) + '</b>, new value <b>' + str(storage_item.amount) + '</b>'
            )
            name_user = request.user.first_name + ' ' + request.user.last_name
            if len(name_user) < 3:
                name_user = request.user.profile.position
            permissions = tuple(['change_storage'])
            chat_message = '<b>'+name_user+'</b> add item <b>' + storage_item.item_name + '</b>'
            new_system_message(request, chat_message, permissions)
            return JsonResponse({
                'error': False,
                'message': 'OK',
                'amount': storage_item.amount
            }, safe=False)
        else:
            return JsonResponse({
                'error': True,
                'message': 'You try do unknown action.',
            }, safe=False)
    else:
        return JsonResponse({
            'error': True,
            'message': 'You don\'t have permissions for this acton.',
        }, safe=False)


def change_price(request):
    if request.user.has_perm('storage.change_storage'):
        if request.POST:
            item_id = request.POST.get('item_id')
            price = float(request.POST.get('price'))
            storage_item = Storage.objects.get(id=item_id)
            history_message = 'Change item <b>' + storage_item.item_name + '</b> price: previous price <b>' + str(storage_item.sell_price) + '</b>'
            storage_item.sell_price = price
            storage_item.save()
            StorageHistory.objects.create(
                user=request.user,
                company_id=request.user.profile.company_id,
                message=history_message + ', new price <b>' + str(storage_item.sell_price) + '</b>'
            )
            name_user = request.user.first_name + ' ' + request.user.last_name
            if len(name_user) < 3:
                name_user = request.user.profile.position
            permissions = tuple(['change_storage'])
            chat_message = '<b>'+name_user+'</b> change price item: <b>' + storage_item.item_name + '</b>'
            new_system_message(request, chat_message, permissions)
            return JsonResponse({
                'error': False,
                'message': 'OK',
            }, safe=False)
        else:
            return JsonResponse({
                'error': True,
                'message': 'You try do unknown action.',
            }, safe=False)
    else:
        return JsonResponse({
            'error': True,
            'message': 'Sorry. You don\'t have permissions for this action.',
        }, safe=False)


def delete_storage_item(request):
    if request.user.has_perm('storage.delete_storage'):
        if request.POST:
            i_id = request.POST.get('id')
            item = Storage.objects.filter(company_id=request.user.profile.company_id).get(id=i_id)
            StorageHistory.objects.create(
                user=request.user,
                company_id=request.user.profile.company_id,
                message='Delete item <b>' + item.item_name + '</b> amount <b>' + str(item.amount) + '</b>, sell price <b>' + str(item.sell_price) + '</b>'
            )
            item.delete()
            name_user = request.user.first_name + ' ' + request.user.last_name
            if len(name_user) < 3:
                name_user = request.user.profile.position
            permissions = tuple(['delete_storage'])
            chat_message = '<b>'+name_user+'</b> delete item <b>' + item.item_name + '</b>'
            new_system_message(request, chat_message, permissions)
            return JsonResponse({
                'error': False,
                'message': 'OK'
            }, safe=False)
        else:
            return JsonResponse({
                'error': True,
                'message': 'You try do undefined action.'
            }, safe=False)
    else:
        return JsonResponse({
            'error': True,
            'message': 'Sorry. You don\'t have permissions for this action.'
        }, safe=False)



def user_equipment(request, id_item):
    user = auth.get_user(request)
    if request.user.has_perm('storage.delete_storage'):
        storage_item = Storage.objects.get(id=id_item)
        workers = User.objects.all().filter(profile__company_id=user.profile.company_id)
        args = {}
        args.update(csrf(request))
        args['user'] = user
        args['username'] = user.username
        args['workers'] = workers
        args['item_name'] = storage_item.item_name
        args['storage_item_id'] = storage_item.id

        return render_to_response('add_equip.html', args)
    else:
        return render_to_response('add_equip.html', {'access_denied': True, 'username': user.username, 'user': user})


def add_user_equipment(request):
    user = auth.get_user(request)
    if request.user.has_perm('storage.add_equipments'):
        if request.POST:
            uids = request.POST.getlist('user_id')
            if len(uids) > 0:
                for u in uids:
                    test = Equipments.objects.filter(storage_item_id=request.POST.get('storage_item_id')).filter(user_id=u)
                    if not test:
                        Equipments.objects.create(
                            user_id=u,
                            storage_item_id=request.POST.get('storage_item_id'),
                            amount=request.POST.get('amount')
                        )
                    else:
                        test[0].amount += float(request.POST.get('amount'))
                        test[0].save()
                    minus = Storage.objects.get(id=request.POST.get('storage_item_id'))
                    minus.amount -= float(request.POST.get('amount'))
                    minus.save()
                    employee = User.objects.get(id=u)
                    StorageHistory.objects.create(
                        user=request.user,
                        company_id=request.user.profile.company_id,
                        message='Add equipment <b>' + minus.item_name + '</b>, amount <b>' + str(request.POST.get('amount')) +
                        '</b> to employee <b>' + employee.first_name + ' ' + employee.last_name + '</b> in storage <b>' + str(minus.amount) + '<b>'
                    )
                    name_user = request.user.first_name + ' ' + request.user.last_name
                    if len(name_user) < 3:
                        name_user = request.user.profile.position
                    permissions = tuple(['add_equipments'])
                    chat_message = '<b>'+name_user+'</b> add equipment <b>' + minus.item_name + '</b>, to employee <b>' + employee.first_name + ' ' + employee.last_name + '</b> '
                    new_system_message(request, chat_message, permissions)
            return JsonResponse({
                'error': False,
                'message': 'OK'
            }, safe=False)
        else:
            return JsonResponse({
                'error': True,
                'message': 'You try do undefined action.'
            }, safe=False)
    else:
        return render_to_response('add_equip.html', {'access_denied': True, 'user': user, 'error': True})


def cancel_equipment_amount(request):
    if request.user.has_perm('storage.change_equipments'):
        uid = request.POST.get('uid', '')
        sid = request.POST.get('sid', '')
        message = request.POST.get('comment', '')
        amount = float(request.POST.get('amount', 0))
        equipment_item = Equipments.objects.filter(user_id=uid).get(storage_item_id=sid)
        inner_message = 'Cancel equipment <b>' + equipment_item.storage_item.item_name + '</b>, amount <b>' + str(amount)
        employee = equipment_item.user
        if equipment_item.amount == amount:
            equipment_item.delete()
            left_amount = 0
        elif equipment_item.amount > amount:
            equipment_item.amount -= amount
            left_amount = equipment_item.amount
            equipment_item.save()
        StorageHistory.objects.create(
            user=request.user,
            company_id=request.user.profile.company_id,
            message= inner_message + '</b> employee <b>' + employee.first_name + ' ' + employee.last_name + '</b>. Left in employee <b>' + str(left_amount) + '.</b> ' + message
        )
        name_user = request.user.first_name + ' ' + request.user.last_name
        if len(name_user) < 3:
            name_user = request.user.profile.position
        permissions = tuple(['change_equipments'])
        chat_message = '<b>'+name_user+'</b> '+inner_message + '</b> employee <b>' + employee.first_name + ' ' + employee.last_name + '</b>. Left in employee <b>' + str(left_amount) + '.</b>'
        new_system_message(request, chat_message, permissions)
        return JsonResponse({
            'error': False
        }, safe=False)
    else:
        return JsonResponse({
            'error': True,
            'message': 'Sorry. You don\'t have permissions for this action.'
        }, safe=False)



def worker_inventory(request):
    if request.POST:
        u_id = request.POST.get('u_id')
        set = Equipments.objects.filter(user_id=u_id)
        stor_list = []
        for i in set:
            stor_list.append({'item_name':i.storage_item.item_name, 'amount':i.amount})
        return HttpResponse(json.dumps(stor_list), content_type='application/json')
    else:
        return HttpResponse('You try do unknown action.')


def inventory_json(request):
    user_id = request.GET.get('id', request.user.id)
    inv = Equipments.objects.filter(user__profile__company_id=request.user.profile.company_id).filter(user_id=user_id)
    list_inv = []
    [list_inv.append({'text':i.storage_item.item_name, 'id':i.id}) for i in inv]
    metod = request.GET.get('for', '')
    res = list_inv
    if metod == 'table':
        list_inv = []
        [list_inv.append(i.as_dict()) for i in inv]
        res = {
            'draw': 1,
            'recordsTotal': len(list_inv),
            'recordsFiltered': len(list_inv),
            'data': list_inv
        }
    elif metod == 'see':
        if request.user.has_perm('billing.add_option'):
            uid = request.GET.get('user', '')
            inv = Equipments.objects.filter(user__profile__company_id=uid).filter(user_id=uid)
            list_inv = []
            [list_inv.append(i.as_dict()) for i in inv]
            res = {
                'draw': 1,
                'recordsTotal': len(list_inv),
                'recordsFiltered': len(list_inv),
                'data': list_inv
            }
    return JsonResponse(res, safe=False)


def get_inuse(request):
    if request.user.has_perm('storage.add_storage') or request.user.has_perm('storage.add_equipments'):
        if request.POST:
            item_id = request.POST.get('item_id')
            items_list = Equipments.objects.filter(storage_item=item_id)
            items_dict = []
            for i in items_list:
                u_name = i.user.first_name + ' ' + i.user.last_name
                items_dict.append({'username': u_name, 'amount': i.amount, 'uid': i.user.id})
            return HttpResponse(json.dumps(items_dict), content_type='application/json')
        else:
            return HttpResponse('You try do unknown action.')
    else:
        return HttpResponse('Sorry. You don\'t have permissions for this action.')


def history(request):
    args = {}
    args.update(csrf(request))
    user = request.user
    args['user'] = user
    args['top_four'] = top_four_elements(request)
    args['company'] = CompanyReg.objects.get(user=user.profile.company_id)
    list_perms = []
    [list_perms.append(i) for i in user.get_all_permissions()]
    args['user_perms'] = list_perms
    if request.user.has_perm('storage.change_storage') or request.user.has_perm('storage.add_storage') or request.user.has_perm('storage.delete_storage') or request.user.has_perm('storage.add_equipments'):
        workers = User.objects.filter(profile__company_id=request.user.profile.company_id).filter(profile__hidden=False).order_by('first_name', 'last_name')
        args['workers'] = workers
    else:
        args['access_denied'] = True
    return render_to_response('storage_history.html', args)


def storage_history_json(request):
    history_list = []
    sh = StorageHistory.objects.filter(company_id=request.user.profile.company_id).order_by('-date')
    search = request.GET.get('search', '')
    if search:
        employee_list = request.GET.getlist('employee', '')
        if employee_list:
            employee_list=tuple(employee_list)
            filtered_sh = sh.filter(user__id__in=employee_list)
            sh = filtered_sh
        message_text = request.GET.get('m-text', '')
        if message_text:
            filtered_sh = sh.filter(message__icontains=message_text)
            sh = filtered_sh
        date = request.GET.get('date-range', '').split(' - ')
        ignore_date = request.GET.get('ignore-date', 'ignore')
        if ignore_date != 'on' and ignore_date != '':
            if len(date) > 0:
                start_date = date[0].split('/')[0] + '-' + date[0].split('/')[1] + '-' + date[0].split('/')[2]
                end_date = date[1].split('/')[0] + '-' + date[1].split('/')[1] + '-' + date[1].split('/')[2]
                if start_date != end_date:
                    filtered_sh = sh.filter(date__date__range=(start_date, end_date))
                else:
                    filtered_sh = sh.filter(date__date=start_date)
                sh = filtered_sh
    if sh:
        for h in sh:
            history_list.append(h.as_dict())
    else:
        history_list=[]
    return JsonResponse({
        'draw': 1,
        'totalRecords': len(history_list),
        'filteredRecords': len(history_list),
        'data': history_list
    }, safe=False)
