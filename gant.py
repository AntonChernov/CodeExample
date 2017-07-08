from django.shortcuts import render, render_to_response
from django.template.context_processors import csrf
from django.contrib import auth
from loginsys.models import CompanyReg
from schedule.models import Task, TaskStatus
from yarn.settings import DEBUG, ALLOWED_HOSTS
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
import datetime
from django.utils import timezone
from  django.contrib.auth.models import User
from company.views import top_four_elements


def gant_intro(request):
    user = auth.get_user(request)
    args = {}
    args.update(csrf(request))
    args['company'] = CompanyReg.objects.get(user=user.profile.company_id)
    args['user'] = user
    if user.id != user.profile.company_id:
        args['userid'] = user.id
        args['username'] = user.first_name+' '+user.last_name
    args['top_four'] = top_four_elements(request)
    args['statuses'] = TaskStatus.objects.all()
    now = timezone.now()
    args['now'] = now.strftime("%Y, "+str(now.month-1)+", %d, %H")
    start_day = now - datetime.timedelta(days=30)
    end_day = now + datetime.timedelta(days=15)
    args['start_day'] = start_day.strftime("%Y-%m-%d")
    args['end_day'] = end_day.strftime("%Y-%m-%d")
    list_perms = []
    [list_perms.append(i) for i in user.get_all_permissions()]
    args['user_perms'] = list_perms
    if DEBUG == True:
        args['path'] = ALLOWED_HOSTS[1]+':8000'
    else:
        args['path'] = ALLOWED_HOSTS[-1]
    if request.user.has_perm('schedule.see_task') or request.user.has_perm('schedule.add_task') or request.user.has_perm('schedule.change_task') or request.user.has_perm('schedule.delete_task'):
        return render_to_response('gantt_template.html', args)
    else:
        args['access_denied'] = True
        return render_to_response('gantt_template.html', args)

def gant_info(request):
    user = auth.get_user(request)
    #tstat = TaskStatus.objects.get(name='closed')
    tasks = Task.objects.filter(company_id=user.profile.company_id)
    task = []
    [task.append(i.as_dict()) for i in tasks]
    filter_ = request.GET.get('filter')

    return JsonResponse(task, safe=False)


def gantt_info_json(request):
    user = auth.get_user(request)
    tasks = Task.objects.filter(company_id=user.profile.company_id)
    try:
        ostat = TaskStatus.objects.get(name='new')
    except ObjectDoesNotExist:
        ostat = TaskStatus.objects.create(name='new')
    try:
        cstat = TaskStatus.objects.get(name='closed')
    except ObjectDoesNotExist:
        cstat = TaskStatus.objects.create(name='closed')
    try:
        instat = TaskStatus.objects.get(name='processing')
    except ObjectDoesNotExist:
        instat = TaskStatus.objects.create(name='processing')
    fr = request.GET.get('filter')
    result_list = []
    if fr == 'all':
        [result_list.append(task.as_dict()) for task in tasks]
        return JsonResponse(result_list, safe=False)
    if fr == 'clo':
        tstat = TaskStatus.objects.get(name='closed')
        st_date = datetime.datetime.now()
        ed_date = datetime.timedelta(days=30)
        filt = st_date-ed_date
        [result_list.append(task.as_dict()) for task in tasks.filter(status=tstat.id).filter(
            close_datetime__range=(st_date, filt))]
        return JsonResponse(result_list, safe=False)
    if fr == 'open':
        tstat = TaskStatus.objects.get(name='closed')
        [result_list.append(task.as_dict()) for task in tasks.exclude(status=tstat.id)]
        return JsonResponse(result_list, safe=False)
    if fr == '':
        [result_list.append(task.as_dict()) for task in tasks]
        return JsonResponse(result_list, safe=False)
