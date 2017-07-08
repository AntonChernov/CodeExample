# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.contrib import auth
from django.http import JsonResponse
from django.contrib.auth.models import User, Group, Permission
from django.shortcuts import render_to_response, redirect, HttpResponse
from django.template.context_processors import csrf
from django.core.exceptions import ObjectDoesNotExist
from guardian.shortcuts import get_perms, assign_perm
from staff.models import Profile
import simplejson as json
from loginsys.models import CompanyReg
from storage.models import *
from staff.forms import CreationManagerForm, EditManagerForm
from loginsys.views import first_start
from billing.models import CodeName, UserPlan
from chat.views import new_system_message
from company.views import top_four_elements


# Create your views here.
# Одна вюшка створює всі види працівників

def new_employee(request):
    perm_str = 'staff.add_'
    if request.POST:
        user_plan = UserPlan.objects.get(user=request.user.profile.company_id)
        code_name = CodeName.objects.get(name='employees')
        try:
            employees_count = user_plan.plan.options.get(code_name=code_name.id).amount
        except ObjectDoesNotExist:
            return JsonResponse({
                'error': True,
                'message': 'Sorry. In you plan don\'t have this option.'
            }, safe=False)
        else:
            user_count = auth.get_user(request)
            count_emp = User.objects.all().filter(profile__company_id=user_count.profile.company_id).filter(profile__hidden=False).count()
            if count_emp <= employees_count or employees_count == -1:
                perm_str += request.POST.get('class')
                if request.user.has_perm(perm_str):
                    group_name = request.POST.get('position') + 's'
                    username = request.POST.get('email')
                    first_name = request.POST.get('first_name')
                    last_name = request.POST.get('last_name')
                    email = request.POST.get('email')
                    phone = request.POST.get('phone')
                    another_phone = request.POST.get('another_phone')
                    date_of_birth = request.POST.get('date_of_birth')
                    password = request.POST.get('password')
                    group = Group.objects.get(name=group_name)
                    user = User.objects.create(username=username, email=email)
                    user.set_password(password)
                    user.first_name = first_name
                    user.last_name = last_name
                    user.is_active = True
                    user.groups.add(group)
                    user.save()
                    profile = Profile.objects.create(user=user, phone=phone)
                    profile.another_phone = another_phone
                    if date_of_birth == '':
                        date_of_birth = None
                    profile.date_of_birth = date_of_birth
                    profile.position = request.POST.get('position')
                    profile.company_id = auth.get_user(request).profile.company_id
                    profile.save()
                    uid = user.id
                    list_perms = []
                    list_perms.append(uid)
                    #[list_perms.append(i) for i in request.user.get_all_permissions()]
                    name_user = request.user.first_name + ' ' + request.user.last_name
                    if len(name_user) < 3:
                        name_user = request.user.profile.position
                    permissions = tuple(['add_staf', 'add_manager', 'add_topmanager', 'add_employee'])
                    chat_message = '<b>'+name_user+'</b> create '+profile.position+': '+first_name+' '+last_name
                    new_system_message(request, chat_message, permissions)
                    return JsonResponse({'error': False, 'id':uid}, safe=False)
                else:
                    return JsonResponse({'error': True, 'message': 'Sorry. You don\'t have permission for this action.'}, status=403, safe=False)
            else:
                return JsonResponse({
                    'error': True,
                    'message': 'Sorry. You don\'t have longer create staff.'
                }, safe=False)
    else:
        return JsonResponse({'error': True, 'message': 'Sorry. You try do unknown action.'}, status=404, safe=False)


# Одна вюшка видаляє всі види працівників.
def delete_employee(request):
    perm_str = 'staff.delete_'
    if request.POST:
        perm_str += str(request.POST.get('class'))
        if request.user.has_perm(perm_str):
            uid = request.POST.get('uid')
            if uid:
                user = User.objects.get(id=uid)
                user.profile.hidden = True
                user.profile.save()
                user.save()
                return JsonResponse('OK', safe=False)
        else:
            return JsonResponse('Sorry. You don\'t have permissions for this action.', status=403, safe=False)
    else:
        return JsonResponse('You try do unknown action.', status=404, safe=False)


def delete_user_emloyee(request):
    if request.POST:
        eid = request.POST.get('uid')
        user = User.objects.get(id=eid)
        inventory = Equipments.objects.filter(user_id=eid)
        item_id_list = []
        [item_id_list.append(i.storage_item_id) for i in inventory]
        for i in item_id_list:
            inv = inventory.get(storage_item_id=i)
            stor = Storage.objects.get(id=i)
            stor.amount += float(inv.amount)
            stor.save()
        user.profile.hidden=True
        user.profile.save()
        name_user = request.user.first_name + ' ' + request.user.last_name
        if len(name_user) < 3:
            name_user = request.user.profile.position
        permissions = tuple(['delete_staff'])
        chat_message = '<b>'+name_user+'</b> delete '+user.profile.position+': '+user.first_name+' '+user.last_name
        new_system_message(request, chat_message, permissions)
        return JsonResponse('OK', safe=False)
    else:
        return JsonResponse('Sorry. You don\'t have permissions for this action.', status=403, safe=False)



# Дістає інформацію про працівника і поверає у json форматі.
def get_employee_info(request):
    if request.POST:
        uid = request.POST.get('uid')
        empl = User.objects.get(id=uid)
        perm_str = 'staff.add_' + empl.profile.position.lower()
        if request.user.has_perm(perm_str):
            if empl.profile.date_of_birth:
                date = str(empl.profile.date_of_birth.year) + '.' + str(empl.profile.date_of_birth.month) + '.' + str(empl.profile.date_of_birth.day)
            else:
                date = ''
            employee_dict = {
                'first_name': empl.first_name,
                'last_name': empl.last_name,
                'email': empl.email,
                'phone': empl.profile.phone,
                'another_phone': empl.profile.another_phone,
                'date_of_birth': date
            }
            return JsonResponse(json.dumps(employee_dict), safe=False)
        else:
            return JsonResponse('Sorry, You don\'t have permissions for this action', safe=False, status=403)
    else:
        return JsonResponse('You try do unknown action', safe=False, status=404)


# Змінює інформацію про працівника
def update_employee_info(request):
    if request.POST:
        uid = request.POST.get('uid')
        empl = User.objects.get(id=uid)
        perm_str = 'staff.change_' + empl.profile.position.lower()
        if request.user.has_perm(perm_str):
            empl.first_name = request.POST.get('first_name')
            empl.last_name = request.POST.get('last_name')
            #empl.email = request.POST.get('email')
            empl.username = request.POST.get('email')
            empl.profile.phone = request.POST.get('phone')
            if len(request.POST.get('another_phone')) > 0:
                empl.profile.another_phone = request.POST.get('another_phone')
            else:
                empl.profile.another_phone = None
            if len(request.POST.get('date_of_birth')):
                empl.profile.date_of_birth = request.POST.get('date_of_birth')
            else:
                empl.profile.date_of_birth = None
            empl.profile.save()
            if len(request.POST.get('password')) > 3:
                empl.set_password(request.POST.get('password'))
            empl.save()
            return JsonResponse('OK', safe=False)
        else:
            return JsonResponse('Sorry. You don\'t have permissions for this action', safe=False, status=403)
    else:
        return JsonResponse('You try do unknown action', safe=False, status=404)


def edit_employee_perm(request, id_m = None):
    user = auth.get_user(request)
    if request.user.has_perm('loginsys.change_companyreg'):
        all_group = Group.objects.all().exclude(name='Companies')
        user_inf = User.objects.get(id=id_m)
        val_grp = all_group.exclude(name=user_inf.groups.values_list()[0][1])
        id_gr = user_inf.profile.user.groups.values_list()[0][0]
        gr = all_group.get(id=id_gr).permissions.all()
        user_prem_obj = User.objects.get(id=id_m).user_permissions.all()
        non_sort = []
        all_perm = []
        [non_sort.append(j) for i in all_group for j in i.permissions.all()]
        [all_perm.append(i) for i in non_sort if i not in all_perm]
        [all_perm.remove(pr) for pr in gr if pr in all_perm]
        [all_perm.remove(kr) for kr in user_prem_obj if kr in all_perm]
        args = {}
        args.update(csrf(request))
        args['user'] = user
        args['company'] = CompanyReg.objects.get(user=user.profile.company_id)
        args['val_grp'] = val_grp
        args['all_group'] = all_group
        args['user_inf'] = user_inf
        args['user_perm'] = user_prem_obj
        args['all_perm'] = all_perm
        return render_to_response('user_perm.html', args)
    else:
        return render_to_response('user_perm.html', {'access_denied':True, 'user':user, 'username':user.username})


def update_employee_perm(request):
    if request.POST:
        user =User.objects.get(id=request.POST.get('uid'))
        user.user_permissions.clear()
        user.save()
        astr = request.POST.get('astr').split(',')
        new_list_perm = []
        [new_list_perm.append(Permission.objects.get(id=i)) for i in astr if i != '']
        user.user_permissions =new_list_perm
        user.save()
        name_user = request.user.first_name + ' ' + request.user.last_name
        if len(name_user) < 3:
            name_user = request.user.profile.position
        permissions = tuple(['change_manager'])
        chat_message = '<b>'+name_user+'</b> change permissions to '+user.profile.position+': '+user.first_name+' '+user.last_name
        new_system_message(request, chat_message, permissions)
        return HttpResponse('OK')


def change_employee_group(request):
    if request.user.has_perm('staff.change_manager'):
        if request.POST:
            uid = request.POST.get('uid')
            gid = request.POST.get('gid')
            group_name = request.POST.get('group_name')
            user = User.objects.get(id=uid)
            group = Group.objects.get(id=gid)
            user.groups.clear()
            user.groups.add(group)
            pos_dict = {'Employees': 'Employee', 'Managers': 'Manager', 'Topmanagers': 'Top Manager'}
            user.profile.position = pos_dict[group_name]
            user.profile.save()
            user.save()
            name_user = request.user.first_name + ' ' + request.user.last_name
            if len(name_user) < 3:
                name_user = request.user.profile.position
            permissions = tuple(['change_manager'])
            chat_message = '<b>'+name_user+'</b> change '+user.first_name+' '+user.last_name+' position to '+pos_dict[group_name]
            new_system_message(request, chat_message, permissions)
            return HttpResponse('OK')
        else:
            return HttpResponse('You try do unknown action.')
    else:
        return HttpResponse('Sorry. You don\'t have permissions for this action.')


def employees_json(request):
    fl = request.GET.get('filter', 'All')
    for_type = request.GET.get('for', '')
    q = request.GET.get('q', '')
    if request.user.profile.position == 'Director':
        employee_list = Profile.objects.filter(company_id=request.user.profile.company_id).filter(hidden=False)
    elif request.user.has_perm('staff.add_topmanager'):
        if fl == 'All':
            employee_list = Profile.objects.filter(company_id=request.user.profile.company_id).filter(
                hidden=False).exclude(position='Director')
        else:
            employee_list = Profile.objects.filter(company_id=request.user.profile.company_id).filter(
                position=fl).filter(hidden=False)
    elif request.user.has_perm('staff.add_manager'):
        if fl == 'All':
            employee_list = Profile.objects.filter(company_id=request.user.profile.company_id).filter(
                hidden=False).exclude(postion='Topmanager')
        else:
            employee_list = Profile.objects.filter(company_id=request.user.profile.company_id).filter(
                position=fl).filter(hidden=False)
    elif request.user.has_perm('staff.add_employee'):
        if fl == 'All':
            employee_list = Profile.objects.filter(company_id=request.user.profile.company_id).filter(
                position='Employee').filter(hidden=False)
        else:
            employee_list = Profile.objects.filter(company_id=request.user.profile.company_id).filter(
                position=fl).filter(hidden=False)
    else:
        return JsonResponse('You don\'t have permissions for this action', safe=False)

    if for_type == 'select':
        result_list = []
        if q != '':
            first_name = employee_list.filter(user__first_name__icontains=q)
            last_name = employee_list.filter(user__last_name__icontains=q)
            positions = employee_list.filter(position__icontains=q)
            for e in first_name:
                e_dict = {'id': e.user.id, 'text': e.user.first_name + ' ' + e.user.last_name + '(' + e.position + ')'}
                if e_dict not in result_list:
                    result_list.append(e_dict)
            for e in last_name:
                e_dict = {'id': e.user.id, 'text': e.user.first_name + ' ' + e.user.last_name + '(' + e.position + ')'}
                if e_dict not in result_list:
                    result_list.append(e_dict)
            for e in positions:
                e_dict = {'id': e.user.id, 'text': e.user.first_name + ' ' + e.user.last_name + '(' + e.position + ')'}
                if e_dict not in result_list:
                    result_list.append(e_dict)
        else:
            [result_list.append({'id': e.user.id, 'text': e.user.first_name + ' ' + e.user.last_name + '(' + e.position + ')'}) for e in employee_list]
        return JsonResponse(result_list, safe=False)

    result_list = []
    [result_list.append(e.as_dict()) for e in employee_list]
    result_dict = {
        'draw': 1,
        'totalRecords': len(employee_list),
        'filteredRecords': len(employee_list),
        'data': result_list
    }
    return JsonResponse(result_dict, )


def edit_manager(request, id_m):
    user = auth.get_user(request)
    if request.user.has_perm('staff.change_manager'):
        args = {}
        args.update(csrf(request))
        args['user'] = user
        args['username'] = user.username
        manager = User.objects.get(id=id_m)
        initial = {
            'first_name': manager.first_name,
            'last_name': manager.last_name,
            'email': manager.email,
            'phone': manager.profile.phone,
            'another_phone': manager.profile.another_phone,
            'date_of_birth': manager.profile.date_of_birth
        }
        form = EditManagerForm(initial)
        args['form'] = form
        args['manager'] = manager
        return render_to_response('edit_manager.html', args)
    else:
        return render_to_response('edit_manager.html', {'access_denied': True, 'username': user.username, 'user': user})


def edit_top_manager(request, id_m):
    user = auth.get_user(request)
    if request.user.has_perm('staff.change_topmanager'):
        args = {}
        args.update(csrf(request))
        args['user'] = user
        args['username'] = user.username
        manager = User.objects.get(id=id_m)
        initial = {
            'first_name': manager.first_name,
            'last_name': manager.last_name,
            'email': manager.email,
            'phone': manager.profile.phone,
            'another_phone': manager.profile.another_phone,
            'date_of_birth': manager.profile.date_of_birth
        }
        form = EditManagerForm(initial)
        args['form'] = form
        args['manager'] = manager
        return render_to_response('edit_top_manager.html', args)
    else:
        return render_to_response('edit_top_manager.html', {'access_denied': True, 'username': user.username, 'user': user})


def update_manager(request):
    user = auth.get_user(request)
    if request.user.has_perm('staff.change_manager'):
        if request.POST:
            new_manager_form = EditManagerForm(request.POST)
            if new_manager_form.is_valid():
                id_mngr = request.POST.get('id_m')
                #email = new_manager_form.cleaned_data['email']
                first_name = new_manager_form.cleaned_data['first_name']
                last_name = new_manager_form.cleaned_data['last_name']
                phone = new_manager_form.cleaned_data['phone']
                another_phone = new_manager_form.cleaned_data['another_phone']
                date_of = new_manager_form.cleaned_data['date_of_birth']
                password = new_manager_form.cleaned_data['password']
                user = User.objects.get(id=id_mngr)
                if len(password) > 3:
                    user.set_password(raw_password=password)
                #user.email = email
                #user.username = email
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                mgr = Profile.objects.get(user=user)
                mgr.phone = phone
                mgr.another_phone = another_phone
                mgr.date_of_birth = date_of
                mgr.save()
                return redirect('/staff/managers/')
            else:
                return redirect('/staff/managers/')
        else:
            err_update = 'Sorry Cannot update information about manager. Try again. Good luck :))'
            return render_to_response('managers.html', {'error': err_update})
    else:
        return render_to_response('managers.html', {'username': user.username, 'access_denied': True})


def update_top_manager(request):
    user = auth.get_user(request)
    if request.user.has_perm('staff.change_topmanager'):
        if request.POST:
            new_manager_form = EditManagerForm(request.POST)
            if new_manager_form.is_valid():
                id_mngr = request.POST.get('id_m')
                #email = new_manager_form.cleaned_data['email']
                first_name = new_manager_form.cleaned_data['first_name']
                last_name = new_manager_form.cleaned_data['last_name']
                phone = new_manager_form.cleaned_data['phone']
                another_phone = new_manager_form.cleaned_data['another_phone']
                date_of = new_manager_form.cleaned_data['date_of_birth']
                password = new_manager_form.cleaned_data['password']
                user = User.objects.get(id=id_mngr)
                if len(password) > 3:
                    user.set_password(raw_password=password)
                #user.email = email
                #user.username = email
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                mgr = Profile.objects.get(user=user)
                mgr.phone = phone
                mgr.another_phone = another_phone
                mgr.date_of_birth = date_of
                mgr.save()
                return redirect('/staff/top_managers/')
            else:
                return redirect('/staff/top_managers/')
        else:
            err_update = 'Sorry Cannot update information about manager. Try again. Good luck :))'
            return render_to_response('top_managers.html', {'error': err_update})
    else:
        return render_to_response('top_managers.html', {'username': user.username, 'access_denied': True})


def employee(request):
    user = auth.get_user(request)
    args = {}
    args['user'] = user
    args['top_four'] = top_four_elements(request)
    list_perms = []
    [list_perms.append(i) for i in user.get_all_permissions()]
    args['user_perms'] = list_perms
    args['company'] = CompanyReg.objects.get(user=user.profile.company_id)
    user_plan = UserPlan.objects.get(user=request.user.profile.company_id)
    code_name = CodeName.objects.get(name='employees')
    if request.user.has_perm('staff.delete_employee') or request.user.has_perm('staff.add_employee') or request.user.has_perm('staff.change_employee') or request.user.has_perm('staff.see_employee'):
        if request.user.has_perm('staff.add_employee'):
            args['add_staf'] = True
        args['visual_position'] = 'employee'
        args['position'] = 'Employees'
        args['var_position'] = 'employee'
        try:
            employees_count = user_plan.plan.options.get(code_name=code_name.id).amount
        except ObjectDoesNotExist:
            employees_count = 0
        finally:
            employees = User.objects.filter(groups__name__exact='Employees').filter(
                profile__company_id=user.profile.company_id).filter(profile__hidden=False)
            if employees_count >= 0:
                employees = employees.order_by('id')[:employees_count]
            args['employees'] = employees
            return render_to_response('employees.html', args)
    else:
        args['access_denied'] = True
        return render_to_response('employees.html', args)


def managers(request):
    user = auth.get_user(request)
    args = {}
    args['user'] = user
    args['top_four'] = top_four_elements(request)
    list_perms = []
    [list_perms.append(i) for i in user.get_all_permissions()]
    args['user_perms'] = list_perms
    args['company'] = CompanyReg.objects.get(user=user.profile.company_id)
    user_plan = UserPlan.objects.get(user=request.user.profile.company_id)
    code_name = CodeName.objects.get(name='employees')
    if request.user.has_perm('staff.delete_manager') or request.user.has_perm('staff.add_manager') or request.user.has_perm('staff.change_manager') or request.user.has_perm('staff.see_manager'):
        if request.user.has_perm('staff.add_manager'):
            args['add_staf'] = True
        args['position'] = 'Managers'
        args['var_position'] = 'manager'
        args['visual_position'] = 'manager'
        try:
            employees_count = user_plan.plan.options.get(code_name=code_name.id).amount
        except ObjectDoesNotExist:
            employees_count = 0
        finally:
            employees = User.objects.filter(groups__name__exact='Managers').filter(
                profile__company_id=user.profile.company_id).filter(profile__hidden=False)
            if employees_count >= 0:
                employees = employees.order_by('id')[:employees_count]
            args['employees'] = employees
            if request.user.has_perm('staff.change_manager') or request.user.has_perm('staff.delete_manager'):
                args['change_employees'] = True
            return render_to_response('employees.html', args)
    else:
        args['access_denied'] = True
        return render_to_response('employees.html', args)


def top_managers(request):
    user = auth.get_user(request)
    args = {}
    args['user'] = user
    args['top_four'] = top_four_elements(request)
    list_perms = []
    [list_perms.append(i) for i in user.get_all_permissions()]
    args['user_perms'] = list_perms
    args['company'] = CompanyReg.objects.get(user=user.profile.company_id)
    user_plan = UserPlan.objects.get(user=request.user.profile.company_id)
    code_name = CodeName.objects.get(name='employees')
    if request.user.has_perm('staff.delete_topmanager') or request.user.has_perm('staff.change_topmanager') or request.user.has_perm('staff.add_topmanager') or request.user.has_perm('staff.see_topmanager'):
        if request.user.has_perm('staff.add_topmanager'):
            args['add_staf'] = True
        args['position'] = 'Top Managers'
        args['var_position'] = 'topmanager'
        args['visual_position'] = 'top manager'
        try:
            employees_count = user_plan.plan.options.get(code_name=code_name.id).amount
        except ObjectDoesNotExist:
            employees_count = 0
        finally:
            employees = User.objects.filter(groups__name__exact='Topmanagers').filter(
                profile__company_id=user.profile.company_id).filter(profile__hidden=False)
            if employees_count >= 0:
                employees = employees.order_by('id')[:employees_count]
            args['employees'] = employees
            return render_to_response('employees.html', args)
    else:
        args['access_denied'] = True
        return render_to_response('employees.html', args)


def staff(request):
    user = auth.get_user(request)
    users = User.objects.all().filter(profile__company_id=user.profile.company_id).filter(profile__hidden=False)
    user_plan = UserPlan.objects.get(user=request.user.profile.company_id)
    code_name = CodeName.objects.get(name='employees')
    try:
        employees_count = user_plan.plan.options.get(code_name=code_name.id).amount
    except ObjectDoesNotExist:
        employees_count = 0
    finally:
        if employees_count >= 0:
            employees_count += 1
            users = users.order_by('id')[:employees_count]
    workers = []
    prem_top = 0
    prem_m = 0
    prem_e = 0
    if request.user.has_perm('staff.add_topmanager') or request.user.has_perm('staff.see_topmanager') or request.user.has_perm('staff.change_topmanager'):
        prem_top = 1
    if request.user.has_perm('staff.add_manager') or request.user.has_perm('staff.see_manager') or request.user.has_perm('staff.change_manager'):
        prem_m = 1
    if request.user.has_perm('staff.add_employee') or request.user.has_perm('staff.see_employee') or request.user.has_perm('staff.change_employee'):
        prem_e = 1
    for i in users:
        if i.profile.position != 'Director' and i.profile.position != '':
            if prem_top == 1:
                if i.profile.position == 'Topmanager':
                    workers.append(i)
            if prem_m == 1:
                if i.profile.position == 'Manager':
                    workers.append(i)
            if prem_e == 1:
                if i.profile.position == 'Employee':
                    workers.append(i)
        else:
            pass
    args = {}
    args['user'] = user
    args['top_four'] = top_four_elements(request)
    list_perms = []
    [list_perms.append(i) for i in user.get_all_permissions()]
    args['user_perms'] = list_perms
    args['company'] = CompanyReg.objects.get(user=user.profile.company_id)
    args['workers'] = workers
    return render_to_response('all_employess.html', args)



def user_profile_info(request, id_u):
    user = auth.get_user(request)
    args = {}
    args.update(csrf(request))
    args['user'] = user
    list_perms = []
    [list_perms.append(i) for i in user.get_all_permissions()]
    args['user_perms'] = list_perms
    if user.has_perm('staff.change_employee') or user.has_perm('staff.see_employee') or int(id_u) == user.id :

        try:
            user_profile = User.objects.get(id=id_u)
            user_profile.profile
        except ObjectDoesNotExist:
            args['access_denied'] = True
            return render_to_response('user_profile.html', args)
        if user_profile.profile.hidden == False and user_profile.profile.company_id == user.profile.company_id:
            args['empinf'] = user_profile
            if user_profile.profile.position == 'Topmanager':
                if user.has_perm('staff.delete_topmanager'):
                    args['delete_employee']=True
                if user.has_perm('staff.change_topmanager'):
                    args['change_employee']=True
            elif user_profile.profile.position == 'Manager':
                if user.has_perm('staff.delete_manager'):
                    args['delete_employee']=True
                if user.has_perm('staff.change_manager'):
                    args['change_employee']=True
            elif user_profile.profile.position == 'Employee':
                if user.has_perm('staff.delete_employee'):
                    args['delete_employee']=True
                if user.has_perm('staff.change_employee'):
                    args['change_employee']=True
            args['position'] = user.profile.position
            args['user_id'] = user.id
            stor_items = Storage.objects.filter()
            inventory = Equipments.objects.filter(user_id=id_u)
            args['inventory'] = inventory
            initial = {
                'first_name': user_profile.first_name,
                'last_name': user_profile.last_name,
                'email': user_profile.email,
                'phone': user_profile.profile.phone,
                'another_phone': user_profile.profile.another_phone,
                'date_of_birth': user_profile.profile.date_of_birth
            }
            all_group = Group.objects.all().exclude(name='Companies')
            user_inf = User.objects.get(id=id_u)
            if user.profile.position == 'Manager':
                    all_group = all_group.exclude(name='Topmanagers')
            elif user.profile.position == 'Employee':
                    all_group = all_group.exclude(name='Topmanagers').exclude(name='Managers')
            val_grp = all_group.exclude(name=user_inf.groups.values_list()[0][1])
            id_gr = user_inf.profile.user.groups.values_list()[0][0]
            try:
                gr = all_group.get(id=id_gr).permissions.all()
            except ObjectDoesNotExist:
                if user.profile.position == 'Director':
                    redirect_url = '/auth/changeinfo/'+ id_u + '/'
                    return redirect(redirect_url)
                else:
                    args['access_denied'] = True
                    return render_to_response('user_profile.html', args)
            user_prem_obj = User.objects.get(id=id_u).user_permissions.all()
            non_sort = []
            all_perm = []
            [non_sort.append(j) for i in all_group for j in i.permissions.all()]
            [all_perm.append(i) for i in non_sort if i not in all_perm]
            [all_perm.remove(pr) for pr in gr if pr in all_perm]
            [all_perm.remove(kr) for kr in user_prem_obj if kr in all_perm]
            args['company'] = CompanyReg.objects.get(user=user.profile.company_id)
            args['storage'] = Storage.objects.filter(company_id=user.profile.company_id)
            args['val_grp'] = val_grp
            args['all_group'] = all_group
            args['user_inf'] = user_inf
            args['user_perm'] = user_prem_obj
            args['all_perm'] = all_perm
            args['st_inv'] = Profile.objects.get(user_id=id_u)
            form = EditManagerForm(initial)
            args['form'] = form
            args['workers'] = User.objects.filter(profile__company_id=user.profile.company_id)
            args['access_denied'] = False
            return render_to_response('user_profile.html', args)
        else:
            args['access_denied'] = True
            return render_to_response('user_profile.html', args)
    else:
        args['access_denied'] = True
        return render_to_response('user_profile.html', args)


def change_user_profile_info(request):
    user = auth.get_user(request)
    args = {}
    args.update(csrf(request))
    list_perms = []
    [list_perms.append(i) for i in user.get_all_permissions()]
    args['user_perms'] = list_perms
    args['user'] = user
    args['company'] = CompanyReg.objects.get(user=user.profile.company_id)
    if user.has_perm('staff.change_employee'):
        if request.POST:
            uid = request.POST.get('uid')
            user_profile = User.objects.get(id=uid)
            user_profile.first_name = request.POST.get('first_name')
            user_profile.last_name = request.POST.get('last_name')
            user_profile.profile.phone = request.POST.get('phone')
            user_profile.profile.another_phone = request.POST.get('another_phone')
            #user_profile.email = request.POST.get('email')
            #user_profile.username = request.POST.get('email')
            if request.POST.get('date_of_birth') != '':
                user_profile.profile.date_of_birth = request.POST.get('date_of_birth')
            user_profile.profile.save()
            user_profile.save()
            name_user = request.user.first_name + ' ' + request.user.last_name
            if len(name_user) < 3:
                name_user = request.user.profile.position
            permissions = tuple(['change_employee'])
            chat_message = '<b>'+name_user+'</b> cahnge iformation '+user_profile.profile.position+': '+user_profile.first_name+' '+user_profile.last_name
            new_system_message(request, chat_message, permissions)
            return redirect('/staff/employees_list/')
        else:
            err_update = 'Sorry Cannot update information.'
            return render_to_response('user_profile.html', {'error': err_update})
    else:
        args['access_denied'] = True
        return render_to_response('user_profile.html', args)


def change_pl_save(request):
    user = auth.get_user(request)
    args = {}
    if user.has_perm('staff.change_employee'):
        if request.method == 'POST':
            us_prof = User.objects.get(id=request.POST.get('uid'))
            if request.POST.get('choice_') == '':
                us_prof.profile.is_storage = 0
                us_prof.profile.save()
            elif request.POST.get('choice_') == '1':
                us_prof.profile.is_storage = 1
                us_prof.profile.save()
            else:
                us_prof.profile.is_storage = 0
                us_prof.profile.save()
            return redirect('/staff/employees_list/')
        else:
            args['error'] = 'Unknown action!!!'
            render_to_response('user_profile.html', args)
    else:
        args['error'] = 'Access denied!!!!!'
        render_to_response('user_profile.html', args)


def emploues_pass_shange(request):
    user = auth.get_user(request)
    args = {}
    if user.has_perm('staff.add_employee'):
        if request.method == 'POST':
            us = User.objects.get(id=request.POST.get('u_id'))
            if len(request.POST.get('password')) > 3:
                us.set_password(request.POST.get('password'))
                us.save()
                return redirect('/staff/user_profile/'+request.POST.get('u_id')+'/')
        else:
            args['error'] = 'Unknown action'
            return render_to_response('user_profile.html', args)
    else:
        args['access_denied'] = True
        args['error'] = 'You have no permissions for this action!'
        return render_to_response('user_profile.html', args)


def plus(request):
    if request.POST:
        storage_item = Storage.objects.get(id=request.POST.get('stor_it_id'))
        item = Equipments.objects.filter(storage_item_id=request.POST.get('stor_it_id')).filter(user_id=request.POST.get('u_id'))
        it = item.get(user_id=request.POST.get('u_id'))
        it.amount += float(request.POST.get('amount'))
        it.save()
        storage_item.amount -= float(request.POST.get('amount'))
        storage_item.save()
        employee = User.objects.get(id=request.POST.get('u_id'))
        StorageHistory.objects.create(
            user=request.user,
            company_id=request.user.profile.company_id,
            message='Add equipment <b>' + storage_item.item_name + '</b>, amount <b>' + str(request.POST.get('amount')) +
            '</b> to employee <b>' + employee.first_name + ' ' + employee.last_name + '</b> in storage <b>' + str(storage_item.amount) + "</b>"
        )
        name_user = request.user.first_name + ' ' + request.user.last_name
        if len(name_user) < 3:
            name_user = request.user.profile.position
        permissions = tuple(['change_equipments'])
        chat_message = '<b>'+name_user+'</b> add equipment <b>' + storage_item.item_name + '</b>, amount <b>' + str(request.POST.get('amount'))
        chat_message += '</b> to employee <b>' + employee.first_name + ' ' + employee.last_name + '</b> in storage <b>' + str(storage_item.amount) + "</b>"
        new_system_message(request, chat_message, permissions)
        ret_list = []
        ret_list.append(it.amount)
        ret_list.append(storage_item.amount)
        return JsonResponse(ret_list, safe=False)
    else:
        return JsonResponse('You try do unknown action', safe=False, status=404)


def minus(request):
    if request.POST:
        storage_item = Storage.objects.get(id=request.POST.get('stor_it_id'))
        item = Equipments.objects.filter(storage_item_id=request.POST.get('stor_it_id'))
        it=item.get(user_id=request.POST.get('u_id'))
        it.amount -= float(request.POST.get('amount'))
        it.save()
        storage_item.amount += float(request.POST.get('amount'))
        storage_item.save()
        employee = User.objects.get(id=request.POST.get('u_id'))
        StorageHistory.objects.create(
            user=request.user,
            company_id=request.user.profile.company_id,
            message='Minus equipment <b>' + storage_item.item_name + '</b>, amount <b>' + str(request.POST.get('amount')) +
            '</b> to employee <b>' + employee.first_name + ' ' + employee.last_name + '</b> in storage <b>' + str(storage_item.amount) + '</b>'
        )
        name_user = request.user.first_name + ' ' + request.user.last_name
        if len(name_user) < 3:
            name_user = request.user.profile.position
        permissions = tuple(['change_equipments'])
        chat_message = '<b>'+name_user+'</b> minus equipment <b>' + storage_item.item_name + '</b>, amount <b>' + str(request.POST.get('amount'))
        chat_message += '</b> to employee <b>' + employee.first_name + ' ' + employee.last_name + '</b> in storage <b>' + str(storage_item.amount) + '</b>'
        new_system_message(request, chat_message, permissions)
        minus_list = []
        minus_list.append(it.amount)
        minus_list.append(storage_item.amount)
        return JsonResponse(minus_list, safe=False)
    else:
        return JsonResponse('You try do unknown action', safe=False, status=404)


def return_to_storage(request):
    if request.POST:
        usr_item = Equipments.objects.filter(storage_item_id=request.POST.get('stor_it_id'))
        it = usr_item.get(user_id=request.POST.get('u_id'))
        stor = Storage.objects.get(id=request.POST.get('stor_it_id'))
        stor.amount += it.amount
        stor.save()
        employee = User.objects.get(id=request.POST.get('u_id'))
        StorageHistory.objects.create(
            user=request.user,
            company_id=request.user.profile.company_id,
            message='Return to storage item <b>' + stor.item_name + '</b> from employee <b>' + employee.first_name + ' ' + employee.last_name + '</b> amount <b>' + str(it.amount) + '</b>. In storage amount <b>' + str(stor.amount) + '</b>'
        )
        it.delete()
        return_list = [stor.amount]
        name_user = request.user.first_name + ' ' + request.user.last_name
        if len(name_user) < 3:
            name_user = request.user.profile.position
        permissions = tuple(['add_invoice', 'change_invoice', 'delete_invoice'])
        chat_message = '<b>'+name_user+'</b> return to storage item <b>' + stor.item_name + '</b> from employee <b>' + employee.first_name + ' ' + employee.last_name + '</b> amount <b>' + str(it.amount) + '</b>. In storage amount <b>' + str(stor.amount) + '</b>'
        new_system_message(request, chat_message, permissions)
        return JsonResponse(return_list, safe=False)
    else:
        return JsonResponse('You try do unknown action', safe=False, status=404)


def add_equip_user(request):
    if request.POST:
        perm = False
        if request.user.has_perm('storage.add_equipments'):
            perm = True
        storage_item_id = int(request.POST.get('stor_it_id', -1))
        amount = request.POST.get('amount', '')
        if amount == '':
            item_amount = 0
        else:
            item_amount = float(amount)
        if item_amount > 0:
            user_id = int(request.POST.get('u_id', -1))
            stor_it = Storage.objects.get(id=storage_item_id)
            stor_it.amount -= item_amount
            stor_it.save()
            try:
                equip = Equipments.objects.filter(storage_item_id=storage_item_id).get(user_id=user_id)
            except ObjectDoesNotExist:
                equip = Equipments.objects.create(
                    amount=item_amount,
                    storage_item_id=storage_item_id,
                    user_id=user_id
                )
                equip.save()
                list_equip = [equip.storage_item_id, float(stor_it.amount), equip.id]
                return JsonResponse({'data':json.dumps(list_equip), 'perm':perm}, safe=False)
            equip.amount += item_amount
            equip.save()
            employee = User.objects.get(id=request.POST.get('u_id'))
            stor = Storage.objects.get(id=storage_item_id)
            StorageHistory.objects.create(
                user=request.user,
                company_id=request.user.profile.company_id,
                message='Add item to equipment <b>' + stor.item_name + '</b> to employee <b>' + employee.first_name + ' ' + employee.last_name + '</b> amount <b>' + str(item_amount) + '</b>. In storage amount <b>' + str(stor.amount) + '</b>'
            )
            name_user = request.user.first_name + ' ' + request.user.last_name
            if len(name_user) < 3:
                name_user = request.user.profile.position
            permissions = tuple(['change_equipments', 'add_equipments'])
            chat_message = '<b>'+name_user+'</b> add item to equipment <b>' + stor.item_name + '</b> to employee <b>' + employee.first_name + ' ' + employee.last_name + '</b> amount <b>' + str(item_amount) + '</b>. In storage amount <b>' + str(stor.amount) + '</b>'
            new_system_message(request, chat_message, permissions)
            list_equip = [equip.storage_item_id, float(stor_it.amount), equip.id]
            return JsonResponse({'data':json.dumps(list_equip), 'perm':perm}, safe=False)
        else:
            return JsonResponse(json.dumps([0, 0, 0]), safe=False)
    else:
        return JsonResponse('You try do unknown action', safe=False, status=404)


def emp_email_test(request):
    email = request.GET['email']
    try:
        User.objects.get(email=email)
    except ObjectDoesNotExist:
        return JsonResponse('true', safe=False)
    return JsonResponse('This email is already registered!', safe=False)
