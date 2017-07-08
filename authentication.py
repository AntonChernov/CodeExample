
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect, HttpResponse
from django.template.context_processors import csrf
from loginsys.forms import *
from billing.models import CodeName, UserChangesHistory
from loginsys.models import *
from company.models import PaymentMethods, InvoiceStatus
import re, os
from yarn.settings import BASE_DIR
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.core.mail import send_mail
import hashlib, datetime, random
from django.utils import timezone
from staff.models import Profile
from guardian.shortcuts import assign_perm
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from yarn.settings import ALLOWED_HOSTS, DEBUG
from billing.models import UserPlan, UserPlanHistory, Plan, CodeName, PlanOption
from company.views import top_four_elements


def sync_perms():
# Permissions for Companies
    list_company_perms = [
        'loginsys.change_companyreg',
        'staff.see_export',
        'staff.add_topmanager',
        'staff.add_manager',
        'staff.add_employee',
        'staff.change_topmanager',
        'staff.change_manager',
        'staff.change_employee',
        'staff.delete_topmanager',
        'staff.delete_manager',
        'staff.delete_employee',
        'company.add_tax',
        'company.add_item',
        'company.add_client',
        'company.add_estimate',
        'company.add_invoice',
        'company.add_estimateitem',
        'company.add_estimateimage',
        'company.add_invoiceitem',
        'company.add_invoiceimage',
        'company.add_estimateconsumables',
        'company.add_invoiceconsumables',
        'company.add_payment',
        'company.add_paymenthistory',
        'company.add_clientgroup',
        'company.add_referralitems',
        'company.change_tax',
        'company.change_item',
        'company.change_client',
        'company.change_estimate',
        'company.change_invoice',
        'company.change_estimateitem',
        'company.change_estimateimage',
        'company.change_invoiceitem',
        'company.change_estimateconsumables',
        'company.change_invoiceconsumables',
        'company.change_payment',
        'company.change_clientgroup',
        'company.change_referralitems',
        'company.delete_tax',
        'company.delete_item',
        'company.delete_client',
        'company.delete_estimate',
        'company.delete_invoice',
        'company.delete_estimateitem',
        'company.delete_invoiceitem',
        'company.delete_estimateconsumables',
        'company.delete_invoiceconsumables',
        'company.delete_invoiceimage',
        'company.delete_clientgroup',
        'company.delete_referralitems',
        'storage.add_storage',
        'storage.change_storage',
        'storage.delete_storage',
        'storage.add_equipments',
        'storage.change_equipments',
        'storage.delete_equipments',
        'schedule.add_task',
        'schedule.see_task',
        'schedule.change_task',
        'schedule.delete_task',
        'schedule.add_taskcomment',
        'schedule.change_taskcomment',
        'schedule.delete_taskcomment',
        'schedule.add_taskstatus',
        'schedule.change_taskstatus'
    ]

# Permissions for Top Managers
    list_topmanager_perms = [
        'staff.see_export',
        'staff.see_topmanager',
        'staff.add_manager',
        'staff.add_employee',
        'staff.change_manager',
        'staff.change_employee',
        'staff.delete_manager',
        'staff.delete_employee',
        'company.add_tax',
        'company.add_item',
        'company.add_client',
        'company.add_estimate',
        'company.add_invoice',
        'company.add_estimateitem',
        'company.add_estimateimage',
        'company.add_invoiceitem',
        'company.add_invoiceimage',
        'company.add_estimateconsumables',
        'company.add_invoiceconsumables',
        'company.add_payment',
        'company.add_paymenthistory',
        'company.add_clientgroup',
        'company.add_referralitems',
        'company.change_tax',
        'company.change_item',
        'company.change_client',
        'company.change_estimate',
        'company.change_invoice',
        'company.change_estimateitem',
        'company.change_estimateimage',
        'company.change_invoiceitem',
        'company.change_estimateconsumables',
        'company.change_invoiceconsumables',
        'company.change_payment',
        'company.change_clientgroup',
        'company.change_referralitems',
        'company.delete_tax',
        'company.delete_item',
        'company.delete_client',
        'company.delete_estimate',
        'company.delete_invoice',
        'company.delete_estimateitem',
        'company.delete_invoiceitem',
        'company.delete_estimateconsumables',
        'company.delete_invoiceconsumables',
        'company.delete_invoiceimage',
        'company.delete_clientgroup',
        'company.delete_referralitems',
        'storage.add_storage',
        'storage.change_storage',
        'storage.delete_storage',
        'storage.add_equipments',
        'storage.change_equipments',
        'storage.delete_equipments',
        'schedule.add_task',
        'schedule.see_task',
        'schedule.change_task',
        'schedule.delete_task',
        'schedule.add_taskcomment',
        'schedule.change_taskcomment',
        'schedule.delete_taskcomment',
        'schedule.add_taskstatus',
        'schedule.change_taskstatus'
    ]

# Permissions for Managers
    list_manager_perms = [
        'staff.see_export',
        'staff.see_manager',
        'staff.see_employee',
        'company.add_tax',
        'company.add_client',
        'company.add_estimate',
        'company.add_invoice',
        'company.add_estimateitem',
        'company.add_estimateimage',
        'company.add_invoiceitem',
        'company.add_invoiceimage',
        'company.add_estimateconsumables',
        'company.add_invoiceconsumables',
        'company.add_payment',
        'company.add_clientgroup',
        'company.add_referralitems',
        'company.change_tax',
        'company.change_client',
        'company.change_estimate',
        'company.change_invoice',
        'company.change_estimateitem',
        'company.change_estimateimage',
        'company.change_invoiceitem',
        'company.change_estimateconsumables',
        'company.change_invoiceconsumables',
        'company.change_payment',
        'company.change_clientgroup',
        'company.change_referralitems',
        'company.delete_tax',
        'company.delete_client',
        'company.delete_estimate',
        'company.delete_invoice',
        'company.delete_estimateitem',
        'company.delete_invoiceitem',
        'company.delete_estimateconsumables',
        'company.delete_invoiceconsumables',
        'company.delete_invoiceimage',
        'company.delete_clientgroup',
        'company.delete_referralitems',
        'storage.add_equipments',
        'storage.change_equipments',
        'storage.delete_equipments',
        'schedule.add_task',
        'schedule.see_task',
        'schedule.change_task',
        'schedule.delete_task',
        'schedule.add_taskcomment',
        'schedule.change_taskcomment',
        'schedule.delete_taskcomment',
        'schedule.add_taskstatus',
        'schedule.change_taskstatus'
    ]

# Permissions for Workers
    list_worker_perms = [
        'company.add_tax',
        'company.add_client',
        'company.add_estimate',
        'company.add_invoice',
        'company.add_estimateitem',
        'company.add_estimateimage',
        'company.add_invoiceitem',
        'company.add_invoiceimage',
        'company.add_estimateconsumables',
        'company.add_invoiceconsumables',
        'company.add_payment',
        'company.add_clientgroup',
        'company.add_referralitems',
        'company.change_tax',
        'company.change_client',
        'company.change_estimate',
        'company.change_invoice',
        'company.change_estimateitem',
        'company.change_estimateimage',
        'company.change_invoiceitem',
        'company.change_estimateconsumables',
        'company.change_invoiceconsumables',
        'company.change_clientgroup',
        'company.change_referralitems',
        'company.delete_tax',
        'company.delete_estimateitem',
        'company.delete_invoiceitem',
        'company.delete_estimateconsumables',
        'company.delete_invoiceconsumables',
        'company.delete_invoiceimage',
        'company.delete_referralitems',
        'schedule.add_taskcomment',
        'schedule.change_taskcomment',
        'schedule.delete_taskcomment',
        'schedule.add_taskstatus',
        'schedule.change_taskstatus'
    ]

    try:
        grp_company = Group.objects.get(name='Companies')
    except ObjectDoesNotExist:
        grp_company = Group.objects.create(name='Companies')
    try:
        grp_topmanager = Group.objects.get(name='Topmanagers')
    except ObjectDoesNotExist:
        grp_topmanager = Group.objects.create(name='Topmanagers')
    try:
        grp_manager = Group.objects.get(name='Managers')
    except ObjectDoesNotExist:
        grp_manager = Group.objects.create(name='Managers')
    try:
        grp_wokers = Group.objects.get(name='Employees')
    except ObjectDoesNotExist:
        grp_wokers = Group.objects.create(name='Employees')

    grp_company.permissions.clear()
    for cp in list_company_perms:
        assign_perm(cp, grp_company)

    grp_topmanager.permissions.clear()
    for tp in list_topmanager_perms:
        assign_perm(tp, grp_topmanager)

    grp_manager.permissions.clear()
    for mp in list_manager_perms:
        assign_perm(mp, grp_manager)

    grp_wokers.permissions.clear()
    for wp in list_worker_perms:
        assign_perm(wp, grp_wokers)



    return True


def create_codenames():
    # create code namde
    try:
        CodeName.objects.get(name='employees')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='employees',
            color='#3c8dbc',
            text='Users'
        )
    try:
        CodeName.objects.get(name='clients')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='clients',
            color='#00c0ef',
            text='Customers'
        )
    try:
        CodeName.objects.get(name='estimates')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='estimates',
            color='#00a65a',
            text='Estimates'
        )
    try:
        CodeName.objects.get(name='invoices')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='invoices',
            color='#236378',
            text='Invoices'
        )
    try:
        CodeName.objects.get(name='storage')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='storage',
            color='#605ca8',
            text='Materials'
        )
    try:
        CodeName.objects.get(name='items')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='items',
            color='#f39c12',
            text='Items'
        )
    try:
        CodeName.objects.get(name='tasks')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='tasks',
            color='#D81B60',
            text='Tasks'
        )
    try:
        CodeName.objects.get(name='branding')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='branding',
            color='#783823',
            text='Branding'
        )
        # end create codename
    return True


def create_default_plan():
    try:
        plan = Plan.objects.filter(disabled=False).get(type_plan='free')
    except ObjectDoesNotExist:
        plan = Plan.objects.create(
            name='system',
            duration=30,
            price=0,
            disabled=False,
            type_plan='free'
        )
        for c in CodeName.objects.all():
            plan_option = PlanOption.objects.create(
                code_name=c,
                name=c.name,
                amount=5,
                disabled=False
            )
            plan.options.add(plan_option)
        plan.save()
    return plan


def install(request):
    if not sync_perms():
        return JsonResponse({
            'error': True,
            'message': 'Assign perms failed.'
        }, safe=False)
    if not create_codenames():
        return JsonResponse({
            'error': True,
            'message': 'Creating codenames failed.'
        }, safe=False)
    return JsonResponse({
        'error': False,
        'message': 'Default settings configured successfull.'
    }, safe=False)


def assign_default_plan(request):
    users = User.objects.filter(groups__name='Companies')
    for u in users:
        try:
            user_plan = UserPlan.objects.get(user=u)
        except ObjectDoesNotExist:
            plan = create_default_plan()
            today = datetime.datetime.now().date()
            duration = plan.duration
            if duration == -1:
                duration = 365
            to_day = today + datetime.timedelta(days=duration)
            user_plan = UserPlan.objects.create(
                user=u,
                plan=plan,
                start_date=today,
                end_date=to_day
            )
            user_plan.save()
            user_history = UserPlanHistory.objects.create(
                user=u,
                date=today,
                plan_name=plan.name,
                type_plan=plan.type_plan,
                comment='SYSTEM: User got defoult plan.'
            )
            user_history.save()
    return JsonResponse('OK', safe=False)


def login2(request):
    return render_to_response('login2.html')


def main(request):
    args = {}
    args.update(csrf(request))
    user = auth.get_user(request)
    if request.user.is_authenticated():
        return redirect('/dashboard/')
    else:
        return render_to_response('index.html', args)


def index(request):
    user = auth.get_user(request)
    args = {}
    args.update(csrf(request))
    if user.is_authenticated():
        args = {}
        args['user'] = user
        list_perms = []
        [list_perms.append(i) for i in user.get_all_permissions()]
        args['user_perms'] = list_perms
        args['len'] = len(list_perms)
        try:
            user.profile.company_id
        except AttributeError:
            args['company'] = ''
        else:
            args['company'] = CompanyReg.objects.get(user=user.profile.company_id)
        return render_to_response('company_main.html', args)

    else:
        return render_to_response('index.html', args)




def login(request):
    args = {}
    args.update(csrf(request))
    if request.POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.profile.hidden == False:
                auth.login(request, user)
                return redirect('/dashboard/')

        else:
            args['login_error'] = "Incorrect email or password"
            return render_to_response('login.html', args)
    else:
        return render_to_response('login.html', args)

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/auth/login/')

"""
def register_success(request):
    return render_to_response('register_success.html', {'success':True})
"""

def first_start(create_entries):
# Permissions for Companies
    list_company_perms = [
        'loginsys.change_companyreg',
        'staff.see_export',
        'staff.add_topmanager',
        'staff.add_manager',
        'staff.add_employee',
        'staff.change_topmanager',
        'staff.change_manager',
        'staff.change_employee',
        'staff.delete_topmanager',
        'staff.delete_manager',
        'staff.delete_employee',
        'company.add_tax',
        'company.add_item',
        'company.add_client',
        'company.add_estimate',
        'company.add_invoice',
        'company.add_estimateitem',
        'company.add_estimateimage',
        'company.add_invoiceitem',
        'company.add_invoiceimage',
        'company.add_estimateconsumables',
        'company.add_invoiceconsumables',
        'company.add_payment',
        'company.add_paymenthistory',
        'company.add_clientgroup',
        'company.add_referralitems',
        'company.change_tax',
        'company.change_item',
        'company.change_client',
        'company.change_estimate',
        'company.change_invoice',
        'company.change_estimateitem',
        'company.change_estimateimage',
        'company.change_invoiceitem',
        'company.change_estimateconsumables',
        'company.change_invoiceconsumables',
        'company.change_payment',
        'company.change_clientgroup',
        'company.change_referralitems',
        'company.delete_tax',
        'company.delete_item',
        'company.delete_client',
        'company.delete_estimate',
        'company.delete_invoice',
        'company.delete_estimateitem',
        'company.delete_invoiceitem',
        'company.delete_estimateconsumables',
        'company.delete_invoiceconsumables',
        'company.delete_invoiceimage',
        'company.delete_clientgroup',
        'company.delete_referralitems',
        'storage.add_storage',
        'storage.change_storage',
        'storage.delete_storage',
        'storage.add_equipments',
        'storage.change_equipments',
        'storage.delete_equipments',
        'schedule.add_task',
        'schedule.see_task',
        'schedule.change_task',
        'schedule.delete_task',
        'schedule.add_taskcomment',
        'schedule.change_taskcomment',
        'schedule.delete_taskcomment',
        'schedule.add_taskstatus',
        'schedule.change_taskstatus'
    ]


# Permissions for Top Managers
    list_topmanager_perms = [
        'staff.see_export',
        'staff.see_topmanager',
        'staff.add_manager',
        'staff.add_employee',
        'staff.change_manager',
        'staff.change_employee',
        'staff.delete_manager',
        'staff.delete_employee',
        'company.add_tax',
        'company.add_item',
        'company.add_client',
        'company.add_estimate',
        'company.add_invoice',
        'company.add_estimateitem',
        'company.add_estimateimage',
        'company.add_invoiceitem',
        'company.add_invoiceimage',
        'company.add_estimateconsumables',
        'company.add_invoiceconsumables',
        'company.add_payment',
        'company.add_paymenthistory',
        'company.add_clientgroup',
        'company.add_referralitems',
        'company.change_tax',
        'company.change_item',
        'company.change_client',
        'company.change_estimate',
        'company.change_invoice',
        'company.change_estimateitem',
        'company.change_estimateimage',
        'company.change_invoiceitem',
        'company.change_estimateconsumables',
        'company.change_invoiceconsumables',
        'company.change_payment',
        'company.change_clientgroup',
        'company.change_referralitems',
        'company.delete_tax',
        'company.delete_item',
        'company.delete_client',
        'company.delete_estimate',
        'company.delete_invoice',
        'company.delete_estimateitem',
        'company.delete_invoiceitem',
        'company.delete_estimateconsumables',
        'company.delete_invoiceconsumables',
        'company.delete_invoiceimage',
        'company.delete_clientgroup',
        'company.delete_referralitems',
        'storage.add_storage',
        'storage.change_storage',
        'storage.delete_storage',
        'storage.add_equipments',
        'storage.change_equipments',
        'storage.delete_equipments',
        'schedule.add_task',
        'schedule.see_task',
        'schedule.change_task',
        'schedule.delete_task',
        'schedule.add_taskcomment',
        'schedule.change_taskcomment',
        'schedule.delete_taskcomment',
        'schedule.add_taskstatus',
        'schedule.change_taskstatus'
    ]

# Permissions for Managers
    list_manager_perms = [
        'staff.see_export',
        'staff.see_manager',
        'staff.see_employee',
        'company.add_tax',
        'company.add_client',
        'company.add_estimate',
        'company.add_invoice',
        'company.add_estimateitem',
        'company.add_estimateimage',
        'company.add_invoiceitem',
        'company.add_invoiceimage',
        'company.add_estimateconsumables',
        'company.add_invoiceconsumables',
        'company.add_payment',
        'company.add_clientgroup',
        'company.add_referralitems',
        'company.change_tax',
        'company.change_client',
        'company.change_estimate',
        'company.change_invoice',
        'company.change_estimateitem',
        'company.change_estimateimage',
        'company.change_invoiceitem',
        'company.change_estimateconsumables',
        'company.change_invoiceconsumables',
        'company.change_payment',
        'company.change_clientgroup',
        'company.change_referralitems',
        'company.delete_tax',
        'company.delete_client',
        'company.delete_estimate',
        'company.delete_invoice',
        'company.delete_estimateitem',
        'company.delete_invoiceitem',
        'company.delete_estimateconsumables',
        'company.delete_invoiceconsumables',
        'company.delete_invoiceimage',
        'company.delete_clientgroup',
        'company.delete_referralitems',
        'storage.add_equipments',
        'storage.change_equipments',
        'storage.delete_equipments',
        'schedule.add_task',
        'schedule.see_task',
        'schedule.change_task',
        'schedule.delete_task',
        'schedule.add_taskcomment',
        'schedule.change_taskcomment',
        'schedule.delete_taskcomment',
        'schedule.add_taskstatus',
        'schedule.change_taskstatus'
    ]

# Permissions for Workers
    list_worker_perms = [
        'company.add_tax',
        'company.add_client',
        'company.add_estimate',
        'company.add_invoice',
        'company.add_estimateitem',
        'company.add_estimateimage',
        'company.add_invoiceitem',
        'company.add_invoiceimage',
        'company.add_estimateconsumables',
        'company.add_invoiceconsumables',
        'company.add_payment',
        'company.add_clientgroup',
        'company.add_referralitems',
        'company.change_tax',
        'company.change_client',
        'company.change_estimate',
        'company.change_invoice',
        'company.change_estimateitem',
        'company.change_estimateimage',
        'company.change_invoiceitem',
        'company.change_estimateconsumables',
        'company.change_invoiceconsumables',
        'company.change_clientgroup',
        'company.change_referralitems',
        'company.delete_tax',
        'company.delete_estimateitem',
        'company.delete_invoiceitem',
        'company.delete_estimateconsumables',
        'company.delete_invoiceconsumables',
        'company.delete_invoiceimage',
        'company.delete_referralitems',
        'schedule.add_taskcomment',
        'schedule.change_taskcomment',
        'schedule.delete_taskcomment',
        'schedule.add_taskstatus',
        'schedule.change_taskstatus'
    ]

    try:
        PaymentMethods.objects.get(name='Cash')
    except ObjectDoesNotExist:
        PaymentMethods.objects.create(
            name='Cash',
        )
    try:
        PaymentMethods.objects.get(name='Check')
    except ObjectDoesNotExist:
        PaymentMethods.objects.create(
            name='Check',
        )
    try:
        PaymentMethods.objects.get(name='Credit')
    except ObjectDoesNotExist:
        PaymentMethods.objects.create(
            name='Credit',
        )
    try:
        InvoiceStatus.objects.get(name='Paid')
    except ObjectDoesNotExist:
        InvoiceStatus.objects.create(
            name='Paid'
        )
    try:
        InvoiceStatus.objects.get(name='Partial')
    except ObjectDoesNotExist:
        InvoiceStatus.objects.create(
            name='Partial'
        )
    #create code namde
    try:
        CodeName.objects.get(name='employees')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='employees',
            color='#3c8dbc',
            text='Users'
        )
    try:
        CodeName.objects.get(name='clients')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='clients',
            color='#00c0ef',
            text='Customers'
        )
    try:
        CodeName.objects.get(name='estimates')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='estimates',
            color='#00a65a',
            text='Estimates'
        )
    try:
        CodeName.objects.get(name='invoices')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='invoices',
            color='#236378',
            text='Invoices'
        )
    try:
        CodeName.objects.get(name='storage')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='storage',
            color='#605ca8',
            text='Materials'
        )
    try:
        CodeName.objects.get(name='items')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='items',
            color='#f39c12',
            text='Items'
        )
    try:
        CodeName.objects.get(name='tasks')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='tasks',
            color='#D81B60',
            text='Tasks'
        )
    try:
        CodeName.objects.get(name='branding')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='branding',
            color='#783823',
            text='Branding'
        )
    #end create codename
    if create_entries:
        grp_company = Group.objects.create(name='Companies')
        grp_topmanager = Group.objects.create(name='Topmanagers')
        grp_manager = Group.objects.create(name='Managers')
        grp_wokers = Group.objects.create(name='Employees')

        for cp in list_company_perms:
            assign_perm(cp, grp_company)

        for tp in list_topmanager_perms:
            assign_perm(tp, grp_topmanager)

        for mp in list_manager_perms:
            assign_perm(mp, grp_manager)

        for wp in list_worker_perms:
            assign_perm(wp, grp_wokers)
        return None
    else:
        return list_company_perms

"""
def register(request):
    args = {}
    args.update(csrf(request))
    args['form'] = RegistrationForm()
    if request.POST:
        newuser_form = RegistrationForm(request.POST)
        if newuser_form.is_valid():
            newuser_form.save()
            user = User.objects.get(username=newuser_form.cleaned_data['email'])
            try:
                group = Group.objects.get(name='Companies')
            except ObjectDoesNotExist:
                first_start(True)
                group = Group.objects.get(name='Companies')
            user.groups.add(group)
            user.save()
            pr = Profile.objects.create(user=user)
            pr.position = 'Director'
            owner = User.objects.get(username=newuser_form.cleaned_data['email'])
            pr.company_id = owner.id
            pr.save()
            company = CompanyReg.objects.create(user=owner)
            company.company_name = newuser_form.cleaned_data['company_name']
            company.save()
            return render_to_response('register_success.html', {'success':True})
        else:
            args['form'] = newuser_form
    return render_to_response('reg.html', args)
"""

def register(request):
    args = {}
    args.update(csrf(request))
    if request.POST:
        try:
            User.objects.get(email=request.POST.get('email'))
        except ObjectDoesNotExist:
            email = request.POST.get('email')
            salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
            activation_key = hashlib.sha1((str(salt)+str(email)).encode('utf-8')).hexdigest()
            key_expires = timezone.now() + timezone.timedelta(1)
            user = User.objects.create(username=email, email=email)
            try:
                group = Group.objects.get(name='Companies')
            except ObjectDoesNotExist:
                first_start(True)
                group = Group.objects.get(name='Companies')
            user.groups.add(group)
            pass_item = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:12]
            password = ''
            for i in pass_item:
                password += i
            user.set_password(password)
            user.is_active = False
            user.save()
            pr = Profile.objects.create(user=user)
            pr.position = 'Director'
            owner = user.id
            pr.company_id = owner
            pr.save()
            company = CompanyReg(user=user, activation_key=activation_key, key_expires=key_expires)
            company.company_name = request.POST.get('company_name')
            company.save()
            email_subject = 'Registration confirm.'
            if DEBUG == False:
                email_body = "Thanks for registration.(your Login: %s, CHANGE YOUR PASSWORD AFTER CONFIRMATION!!!). To activate your account, click this link within \
                                    24hours http://%s/register/confirm/%s/%s" % (email, ALLOWED_HOSTS[3], activation_key, password)
                send_mail(email_subject, email_body, 'example@gmail.com',
                            [email], fail_silently=False)
                return render_to_response('register_success.html', {'success': True})
            email_body = "Thanks for registration.(your Login: %s, CHANGE YOUR PASSWORD AFTER CONFIRMATION!!!). To activate your account, click this link within \
                                    24hours http://127.0.0.1:8000/register/confirm/%s/%s" % (email, activation_key, password)
            send_mail(email_subject, email_body, 'example@gmail.com',
                            [email], fail_silently=False)
            return render_to_response('register_success.html', {'success': True})
    return render_to_response('index.html', args)


def email_test(request):
    #if request.is_ajax():
    email = request.GET['email']
    try:
        User.objects.get(username=email)
    except ObjectDoesNotExist:
        return JsonResponse('true', safe=False)
    return JsonResponse('This email is already registered!', safe=False)


def register_confirm(request, activation_key, pas):
    user_profile = get_object_or_404(CompanyReg, activation_key=activation_key)
    if user_profile.user.is_active:
        return redirect('/')
    if user_profile.key_expires < timezone.now():
        usr = User.objects.get(id=user_profile.user_id)
        pass_item = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()
        ps = random.sample(pass_item, 8)
        password = ''
        for i in ps:
            password += i
        usr.set_password(password)
        usr.save()
        email = usr.email
        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        activation_key = hashlib.sha1((str(salt)+str(email)).encode('utf-8')).hexdigest()
        user_profile.activation_key = activation_key
        user_profile.key_expires = timezone.now() + timezone.timedelta(1)
        user_profile.save()
        email_subject = 'New conformation linc.'
        if DEBUG==False:
            email_body = "NEW CONFORMATION LINC.(your Login: %s, CHANGE YOUR PASSWORD AFTER CONFIRMATION!!!). To activate your account, click this link within \
                                    24hours http://%s/register/confirm/%s/%s" % (email, ALLOWED_HOSTS[3], activation_key, password)
            send_mail(email_subject, email_body, 'example@gmail.com',
                        [email], fail_silently=False)
            return render_to_response('confirm_expired.html')
        email_body = "NEW CONFORMATION LINC.(your Login: %s, CHANGE YOUR PASSWORD AFTER CONFIRMATION!!!). To activate your account, click this link within \
                                    24hours http://127.0.0.1:8000/register/confirm/%s/%s" % (email, activation_key, password)
        send_mail(email_subject, email_body, 'example@gmail.com',
                        [email], fail_silently=False)
        return render_to_response('confirm_expired.html')
    usr = User.objects.get(id=user_profile.user_id)
    plan = create_default_plan()
    today = datetime.datetime.now().date()
    duration = plan.duration
    if duration == -1:
        duration = 365
    to_day = today + datetime.timedelta(days=duration)
    try:
        user_plan = UserPlan.objects.get(user=usr)
    except ObjectDoesNotExist:
        user_plan = UserPlan.objects.create(
            user=usr,
            plan=plan,
            start_date=today,
            end_date=to_day
        )
        user_plan.save()
    user_history = UserPlanHistory.objects.create(
        user=usr,
        date=today,
        plan_name=plan.name,
        type_plan=plan.type_plan,
        comment='SYSTEM: User confirm registration.'
    )
    user_history.save()
    login_usr = auth.authenticate(username=user_profile.user.username, password=pas)
    user_profile.user.is_active = True
    user_profile.user.save()
    auth.login(request, login_usr)
    return redirect('/register/changepass/%i/?p=%s' % (user_profile.user_id, pas))


"""
def register_ok(request):
    return render_to_response('confirm.html')
"""
def reset_password(request):
    args = {}
    args.update(csrf(request))
    args['form'] = ResetPasswordForm()
    if request.POST:
        reset_pass_form = ResetPasswordForm(request.POST)
        if reset_pass_form.is_valid():
            user = User.objects.get(username=reset_pass_form.cleaned_data['username'])
            email = user.email
            pass_item = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()
            ps = random.sample(pass_item, 8)
            password = ''
            for i in ps:
                password += i
            user.set_password(password)
            user.save()
            email_subject = 'Confirmation of restoration password'
            email_body = """Hey %s, thanks for using our restoration password system.
            To find your new password(%s), go to the email that you used when registering the company. """ % (user.username, password)
            send_mail(email_subject, email_body, 'example@gmail.com',[email], fail_silently=True)
            return render_to_response('reset_success.html', {'success':True, 'email':email})
        else:
            args['form'] = reset_pass_form
    return render_to_response('res_pas.html', args)


def change_company_pass(request, id_company):
    user = auth.get_user(request)
    args = {}
    args.update(csrf(request))
    args['user'] = user
    args['username'] = user.username
    args['company'] = CompanyReg.objects.get(user=user.profile.company_id)
    list_perms = []
    [list_perms.append(i) for i in user.get_all_permissions()]
    args['user_perms'] = list_perms
    if request.user.has_perm('loginsys.change_companyreg'):
        args['old_password'] = request.GET.get('p', '')
        if request.POST:
            old_password = request.POST.get('old_password', '')
            if old_password == '':
                return JsonResponse({
                    'error': True,
                    'message': 'Please enter old password.'
                }, safe=False)
            password1 = request.POST.get('id_password', '')
            password2 = request.POST.get('id_password2', '')
            if password1 != password2 or password1 == '' or password2 == '':
                return JsonResponse({
                    'error': True,
                    'message': 'Passwords are empty or mismatch.'
                }, safe=False)
            elif password1 == password2:
                user = auth.authenticate(username=user.username, password=old_password)
                if user is not None and user.profile.hidden == False:
                    company = User.objects.get(id=user.profile.company_id)
                    company.set_password(password1)
                    company.save()
                    auth.logout(request)
                    UserChangesHistory.objects.create(
                        user=user,
                        message='C  hange password',
                        company_id=user.profile.company_id
                    )
                    return JsonResponse({'error': False}, safe=False)
                else:
                    return JsonResponse({
                        'error': True,
                        'message': 'Invalid old password.'
                    }, safe=False)
        else:
            return render_to_response('change_pass.html', args)
    else:
        args['access_denied'] = True
        return render_to_response('change_pass.html', args)


def change_company_info(request, id_company, *message):
    user = auth.get_user(request)
    args = {}
    args.update(csrf(request))
    if message:
        args['error'] = message[0]
        args['message'] = message[1]
    args['user'] = user
    args['top_four'] = top_four_elements(request)
    #todo
    if user.id == user.profile.company_id:
        u_plan = UserPlan.objects.get(user=request.user)
        args['user_plan'] = u_plan
        args['plans'] = Plan.objects.filter(disabled=False).filter(type_plan='pro')
        args['plan_options'] = u_plan.plan.options.filter(disabled=False)
    args['company'] = CompanyReg.objects.get(user=user.profile.company_id)
    list_perms = []
    [list_perms.append(i) for i in request.user.get_all_permissions()]
    args['user_perms'] = list_perms
    args['img_form'] = ImageUploadForm
    cmp = CompanyReg.objects.get(user=user.profile.company_id)
    if request.user.has_perm('loginsys.change_companyreg'):# and request.user.id == id_company:
        company = User.objects.get(id=id_company)
        cmpn = {
            'company_name':company.companyreg.company_name,
            'email': cmp.worked_email,
            'phone': company.companyreg.phone,
            'contact': company.companyreg.contact,
            'first_name': company.first_name,
            'last_name': company.last_name,
            'offer': cmp.offer,
            'document_start_number': company.companyreg.document_start_number
        }
        args['form'] = ChangeCompanyInfoForm(cmpn)
        args['address'] = cmp
        return render_to_response('edit_company_info.html', args)
    else:
        args['access_denied'] = True
        return render_to_response('edit_company_info.html', args)

def update_company_info(request):
    user = auth.get_user(request)
    args = {}
    args.update(csrf(request))
    args['user'] = auth.get_user(request)
    args['company'] = CompanyReg.objects.get(user=user.profile.company_id)
    if request.POST:
        form_ch = ChangeCompanyInfoForm(request.POST)
        if form_ch.is_valid():
            id_c = request.POST.get('company_id')
            us = User.objects.get(id=id_c)
            new_company_info = CompanyReg.objects.get(user_id=id_c)
            new_company_info.worked_email = request.POST.get('email')
            new_company_info.company_name = request.POST.get('company_name')
            new_company_info.phone = request.POST.get('phone')
            new_company_info.contact = request.POST.get('contact')
            new_company_info.offer = request.POST.get('offer')
            new_company_info.address = request.POST.get('address')
            new_company_info.address2 = request.POST.get('address2')
            new_company_info.city = request.POST.get('city')
            new_company_info.state = request.POST.get('state')
            new_company_info.zip_code = request.POST.get('zip_code')
            #us.username = form_ch.cleaned_data['email']
            us.first_name = request.POST.get('first_name')
            us.last_name = request.POST.get('last_name')
            sa_pl(request, id_c, request.POST.get('radiouset'))
            us.save()
            new_company_info.save()
            return HttpResponseRedirect('/auth/changeinfo/'+str(id_c)+'/')
        else:
            args['form'] = form_ch
            return render_to_response('edit_company_info.html', args)
    else:
        return render_to_response('edit_company_info.html', args)


def em_change(request):
    if request.POST:
        us = User.objects.get(id=request.user.profile.company_id)
        new_company_info = CompanyReg.objects.get(user_id=request.user.profile.company_id)
        email = request.POST.get('email')
        password = request.POST.get('pass')
        login_usr = auth.authenticate(username=us.username, password=password)
        if login_usr is not None and login_usr.profile.hidden == False:
            salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
            activation_key = hashlib.sha1((str(salt)+str(email)).encode('utf-8')).hexdigest()
            pass_item = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()
            us.save()
            new_company_info.temporary_email = email
            new_company_info.activation_key = activation_key
            new_company_info.save()
            email_subject = 'Confirm company e-mail change.'
            args={}
            args['error'] = False
            UserChangesHistory.objects.create(
                user=request.user,
                message='Send email to change email(<b>'+request.user.email+'</b>) to : <b>' + email+'</b>',
                company_id=request.user.profile.company_id
            )
            if DEBUG==False:
                email_body = "NEW CONFORMATION LINC.(your Login: %s, CHANGE YOUR PASSWORD AFTER CONFIRMATION!!!(temporary password: %s)). " \
                             "To activate your account, click this link http://%s/register/confirm_email_change/%s/%s" \
                                 % (email, password, ALLOWED_HOSTS[2], activation_key, password)
                send_mail(email_subject, email_body, 'example@gmail.com',
                            [email], fail_silently=False)
                return render_to_response('company_email_change.html', args)
            email_body = "NEW CONFORMATION LINC.(your Login: %s, CHANGE YOUR PASSWORD AFTER CONFIRMATION!!!). To activate your account, click this link  \
                                         http://127.0.0.1:8000/register/confirm_email_change/%s/%s" % (email, activation_key, password)
            send_mail(email_subject, email_body, 'example@gmail.com',
                        [email], fail_silently=False)
        else:
            args={}
            args['error'] = True
            args['message'] = 'wrong password'
            return render_to_response('company_email_change.html', args)
    return render_to_response('company_email_change.html', args)


def em_change_confirm(request, activation_key, pas):
    user_profile = get_object_or_404(CompanyReg, activation_key=activation_key)
    user_profile.user.email = user_profile.temporary_email
    user = user_profile.user
    login_usr = auth.authenticate(username=user.username, password=pas)
    if login_usr is not None and login_usr.profile.hidden == False:
        user.username = user_profile.temporary_email
        user.save()
        salt = hashlib.sha1(str(random.random()).encode('utf-8')).hexdigest()[:5]
        activation_key = hashlib.sha1((str(salt)+str(user_profile.temporary_email)).encode('utf-8')).hexdigest()
        new_company_info = CompanyReg.objects.get(user_id=user.id)
        new_company_info.activation_key = activation_key
        new_company_info.save()
        auth.logout(request)
        auth.login(request, login_usr)
        UserChangesHistory.objects.create(
            user=request.user,
            message='Confirm change email to : <b>' + user_profile.user.email+'</b>',
            company_id=request.user.profile.company_id
        )
        return redirect('/auth/personal_area/%i/' % login_usr.id)
    else:
        auth.logout(request)
        return redirect('/')

def email_change_confirm(request, activation_key, pas):
    user_profile = get_object_or_404(CompanyReg, activation_key=activation_key)
    user = user_profile.user
    login_usr = auth.authenticate(username=user.username, password=pas)
    user.save()
    auth.login(request, login_usr)
    return redirect('/register/changepass/%i/' % user_profile.id)


def email_emploues_change(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        us = User.objects.get(id=request.POST.get('u_id'))
        us.email = email
        us.username = email
        us.save()
        return redirect('/staff/user_profile/' + str(us.id)+'/')
    return HttpResponse('Bad request!')

def _haslog(f, cid):
    res = re.findall(u'[0-9]\d', str(timezone.now()))
    a = ''
    for i in res:
        a += ''.join(i)
    if os.path.isdir(BASE_DIR + '/static/company_logos/'):
        _r = '/static/company_logos/clg_'+a+f.name
        _route = BASE_DIR+'/static/company_logos/clg_'+a+f.name
        with open(_route, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
        im = CompanyReg.objects.get(user_id=cid)
        if im.logo != _r and im.logo != '/static/company_logos/default-company.png':
            if os.path.exists(BASE_DIR + im.logo):
                os.remove(BASE_DIR + im.logo)
            im.logo = _r
            im.save()
        else:
            im.logo = _r
            im.save()
        _re = im.id
    else:
        os.makedirs(BASE_DIR + '/static/company_logos/')
        _r = '/static/company_logos/clg_'+a+f.name
        _route = BASE_DIR+'/static/company_logos/clg_'+a+f.name
        with open(_route, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
        im = CompanyReg.objects.get(user_id=cid)
        if im.logo != _r and im.logo != '/static/company_logos/default-company.png':
            os.remove(BASE_DIR + im.logo)
            im.logo = _r
            im.save()
        else:
            im.logo = _r
            im.save()



def company_logo(request):
    user = request.user
    args = {}
    args.update(csrf(request))
    list_perms = []
    [list_perms.append(i) for i in user.get_all_permissions()]
    args['user'] = user
    args['user_perms'] = list_perms
    args['company'] = CompanyReg.objects.get(user_id=request.user.profile.company_id)
    if request.POST:
        le = request.FILES.get('image')
        t = _haslog(le, request.user.profile.company_id)
    return redirect('/auth/changeinfo/'+str(request.user.profile.company_id)+'/')


def sync_perm(create_entries):
# Permissions for Companies
    list_company_perms = [
        'loginsys.change_companyreg',
        'staff.see_export',
        'staff.add_topmanager',
        'staff.add_manager',
        'staff.add_employee',
        'staff.change_topmanager',
        'staff.change_manager',
        'staff.change_employee',
        'staff.delete_topmanager',
        'staff.delete_manager',
        'staff.delete_employee',
        'company.add_tax',
        'company.add_item',
        'company.add_client',
        'company.add_estimate',
        'company.add_invoice',
        'company.add_estimateitem',
        'company.add_estimateimage',
        'company.add_invoiceitem',
        'company.add_invoiceimage',
        'company.add_estimateconsumables',
        'company.add_invoiceconsumables',
        'company.add_payment',
        'company.add_paymenthistory',
        'company.add_clientgroup',
        'company.add_referralitems',
        'company.change_tax',
        'company.change_item',
        'company.change_client',
        'company.change_estimate',
        'company.change_invoice',
        'company.change_estimateitem',
        'company.change_estimateimage',
        'company.change_invoiceitem',
        'company.change_estimateconsumables',
        'company.change_invoiceconsumables',
        'company.change_payment',
        'company.change_clientgroup',
        'company.change_referralitems',
        'company.delete_tax',
        'company.delete_item',
        'company.delete_client',
        'company.delete_estimate',
        'company.delete_invoice',
        'company.delete_estimateitem',
        'company.delete_invoiceitem',
        'company.delete_estimateconsumables',
        'company.delete_invoiceconsumables',
        'company.delete_invoiceimage',
        'company.delete_clientgroup',
        'company.delete_referralitems',
        'storage.add_storage',
        'storage.change_storage',
        'storage.delete_storage',
        'storage.add_equipments',
        'storage.change_equipments',
        'storage.delete_equipments',
        'schedule.add_task',
        'schedule.see_task',
        'schedule.change_task',
        'schedule.delete_task',
        'schedule.add_taskcomment',
        'schedule.change_taskcomment',
        'schedule.delete_taskcomment',
        'schedule.add_taskstatus',
        'schedule.change_taskstatus'
    ]


# Permissions for Top Managers
    list_topmanager_perms = [
        'staff.see_export',
        'staff.see_topmanager',
        'staff.add_manager',
        'staff.add_employee',
        'staff.change_manager',
        'staff.change_employee',
        'staff.delete_manager',
        'staff.delete_employee',
        'company.add_tax',
        'company.add_item',
        'company.add_client',
        'company.add_estimate',
        'company.add_invoice',
        'company.add_estimateitem',
        'company.add_estimateimage',
        'company.add_invoiceitem',
        'company.add_invoiceimage',
        'company.add_estimateconsumables',
        'company.add_invoiceconsumables',
        'company.add_payment',
        'company.add_paymenthistory',
        'company.add_clientgroup',
        'company.add_referralitems',
        'company.change_tax',
        'company.change_item',
        'company.change_client',
        'company.change_estimate',
        'company.change_invoice',
        'company.change_estimateitem',
        'company.change_estimateimage',
        'company.change_invoiceitem',
        'company.change_estimateconsumables',
        'company.change_invoiceconsumables',
        'company.change_payment',
        'company.change_clientgroup',
        'company.change_referralitems',
        'company.delete_tax',
        'company.delete_item',
        'company.delete_client',
        'company.delete_estimate',
        'company.delete_invoice',
        'company.delete_estimateitem',
        'company.delete_invoiceitem',
        'company.delete_estimateconsumables',
        'company.delete_invoiceconsumables',
        'company.delete_invoiceimage',
        'company.delete_clientgroup',
        'company.delete_referralitems',
        'storage.add_storage',
        'storage.change_storage',
        'storage.delete_storage',
        'storage.add_equipments',
        'storage.change_equipments',
        'storage.delete_equipments',
        'schedule.add_task',
        'schedule.see_task',
        'schedule.change_task',
        'schedule.delete_task',
        'schedule.add_taskcomment',
        'schedule.change_taskcomment',
        'schedule.delete_taskcomment',
        'schedule.add_taskstatus',
        'schedule.change_taskstatus'
    ]

# Permissions for Managers
    list_manager_perms = [
        'staff.see_export',
        'staff.see_manager',
        'staff.see_employee',
        'company.add_tax',
        'company.add_client',
        'company.add_estimate',
        'company.add_invoice',
        'company.add_estimateitem',
        'company.add_estimateimage',
        'company.add_invoiceitem',
        'company.add_invoiceimage',
        'company.add_estimateconsumables',
        'company.add_invoiceconsumables',
        'company.add_payment',
        'company.add_clientgroup',
        'company.add_referralitems',
        'company.change_tax',
        'company.change_client',
        'company.change_estimate',
        'company.change_invoice',
        'company.change_estimateitem',
        'company.change_estimateimage',
        'company.change_invoiceitem',
        'company.change_estimateconsumables',
        'company.change_invoiceconsumables',
        'company.change_payment',
        'company.change_clientgroup',
        'company.change_referralitems',
        'company.delete_tax',
        'company.delete_client',
        'company.delete_estimate',
        'company.delete_invoice',
        'company.delete_estimateitem',
        'company.delete_invoiceitem',
        'company.delete_estimateconsumables',
        'company.delete_invoiceconsumables',
        'company.delete_invoiceimage',
        'company.delete_clientgroup',
        'company.delete_referralitems',
        'storage.add_equipments',
        'storage.change_equipments',
        'storage.delete_equipments',
        'schedule.add_task',
        'schedule.see_task',
        'schedule.change_task',
        'schedule.delete_task',
        'schedule.add_taskcomment',
        'schedule.change_taskcomment',
        'schedule.delete_taskcomment',
        'schedule.add_taskstatus',
        'schedule.change_taskstatus'
    ]

# Permissions for Workers
    list_worker_perms = [
        'company.add_tax',
        'company.add_client',
        'company.add_estimate',
        'company.add_invoice',
        'company.add_estimateitem',
        'company.add_estimateimage',
        'company.add_invoiceitem',
        'company.add_invoiceimage',
        'company.add_estimateconsumables',
        'company.add_invoiceconsumables',
        'company.add_payment',
        'company.add_clientgroup',
        'company.add_referralitems',
        'company.change_tax',
        'company.change_client',
        'company.change_estimate',
        'company.change_invoice',
        'company.change_estimateitem',
        'company.change_estimateimage',
        'company.change_invoiceitem',
        'company.change_estimateconsumables',
        'company.change_invoiceconsumables',
        'company.change_clientgroup',
        'company.change_referralitems',
        'company.delete_tax',
        'company.delete_estimateitem',
        'company.delete_invoiceitem',
        'company.delete_estimateconsumables',
        'company.delete_invoiceconsumables',
        'company.delete_invoiceimage',
        'company.delete_referralitems',
        'schedule.add_taskcomment',
        'schedule.change_taskcomment',
        'schedule.delete_taskcomment',
        'schedule.add_taskstatus',
        'schedule.change_taskstatus'
    ]

    try:
        grp_company = Group.objects.get(name='Companies')
    except ObjectDoesNotExist:
        grp_company = Group.objects.create(name='Companies')
    try:
        grp_topmanager = Group.objects.get(name='Topmanagers')
    except ObjectDoesNotExist:
        grp_topmanager = Group.objects.create(name='Topmanagers')
    try:
        grp_manager = Group.objects.get(name='Managers')
    except ObjectDoesNotExist:
        grp_manager = Group.objects.create(name='Managers')
    try:
        grp_wokers = Group.objects.get(name='Employees')
    except ObjectDoesNotExist:
        grp_wokers = Group.objects.create(name='Employees')

    grp_company.permissions.clear()
    for cp in list_company_perms:
        assign_perm(cp, grp_company)

    grp_topmanager.permissions.clear()
    for tp in list_topmanager_perms:
        assign_perm(tp, grp_topmanager)

    grp_manager.permissions.clear()
    for mp in list_manager_perms:
        assign_perm(mp, grp_manager)

    grp_wokers.permissions.clear()
    for wp in list_worker_perms:
        assign_perm(wp, grp_wokers)

    # create code namde
    try:
        code_name = CodeName.objects.get(name='employees')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='employees',
            color='#3c8dbc'
        )
    code_name.text = 'Users'
    code_name.save()
    try:
        code_name = CodeName.objects.get(name='clients')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='clients',
            color='#00c0ef'
        )
    code_name.text = 'Customers'
    code_name.save()
    try:
        code_name = CodeName.objects.get(name='estimates')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='estimates',
            color='#00a65a'
        )
    code_name.text = 'Estimates'
    code_name.save()
    try:
        code_name = CodeName.objects.get(name='invoices')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='invoices',
            color='#236378'
        )
    code_name.text = 'Invoices'
    code_name.save()
    try:
        code_name = CodeName.objects.get(name='storage')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='storage',
            color='#605ca8'
        )
    code_name.text = 'Materials'
    code_name.save()
    try:
        code_name = CodeName.objects.get(name='items')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='items',
            color='#f39c12'
        )
    code_name.text = 'Items'
    code_name.save()
    try:
        code_name = CodeName.objects.get(name='tasks')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='tasks',
            color='#D81B60'
        )
    code_name.text = 'Tasks'
    code_name.save()
    try:
        code_name = CodeName.objects.get(name='branding')
    except ObjectDoesNotExist:
        CodeName.objects.create(
            name='branding',
            color='#783823'
        )
    code_name.text = 'Branding'
    code_name.save()
        # end create codename

    return JsonResponse('OK', safe=False)


def change_c_em(request):
    user = request.user
    id = user.profile.company_id
    args = {}
    args.update(csrf(request))
    args['id'] = id
    list_perms = []
    [list_perms.append(i) for i in user.get_all_permissions()]
    args['user'] = user
    args['user_perms'] = list_perms
    args['company'] = CompanyReg.objects.get(user_id=id)
    return render_to_response('personal_area.html', args)


def update_personal_area(request):
    user = auth.get_user(request)
    args = {}
    args.update(csrf(request))
    if user.has_perm('loginsys.change_companyreg'):
        if request.POST:
            company = CompanyReg.objects.get(user_id=request.user.profile.company_id)
            company.company_name = request.POST.get('name')
            company.save()
            return redirect('/')
    else:
        args['access_denied'] = True
        return render_to_response('personal_area.html', args)


def sa_pl(request, id, val):
    user = request.user
    save_place = Profile.objects.get(user_id=id)#request.GET.get('id')
    #request.GET.get('val')
    if val == '0':
        save_place.is_storage = 0
    else:
        save_place.is_storage = 1
    save_place.save()
    data = {
        'val': val
    }
    return JsonResponse(data, safe=False)
