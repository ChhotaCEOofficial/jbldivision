from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import json
import csv
from datetime import datetime
from io import TextIOWrapper
from django.shortcuts import get_object_or_404
from .models import MeBasicEntry, StatsMonthlyEntry
from .forms import MeBasicForm, StatsMonthlyForm


from .models import (
    CustomUser, RailMadadReport, Department, Report,
    UploadLog, JabalpurOperation, DataEntry, ReportData
)
from django.contrib.auth.models import User


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'login.html')


@csrf_exempt
def popup_close(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        request.session['popup_shown'] = True
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'fail'}, status=400)


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    if 'popup_shown' not in request.session:
        request.session['popup_shown'] = False

    show_popup = not request.session['popup_shown']
    recent_reports = Report.objects.order_by('-last_updated')[:5]

    context = {
        'show_popup': show_popup,
        'recent_reports': recent_reports,
    }
    return render(request, 'dashboard.html', context)


@login_required
def clear_cache(request):
    cache.clear()
    messages.success(request, "Cache cleared successfully!")
    return redirect('dashboard')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created successfully! You can now login.")
        return redirect('login')

    return render(request, 'signup.html')


@login_required
def pending_users(request):
    users = CustomUser.objects.filter(is_approved=False)
    return render(request, 'pending_users.html', {'users': users})


@login_required
def approve_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_approved = True
    user.save()
    return redirect('pending_users')


@login_required
def reject_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    return redirect('pending_users')


@login_required
def add_report(request):
    return render(request, 'add_report.html')


@login_required
def admin_panel(request):
    return render(request, 'admin_panel.html')


@login_required
def data_entry(request):
    return render(request, 'data_entry.html')


@login_required
def mis_reports(request):
    return render(request, 'mis_reports.html')

@login_required
def my_reports_view(request):
    departments = ['COA', 'Mech', 'Fois', 'ELEC', 'Security', 'Commercial', 'ICMS', 'ENG', 'TRD', 'S&T', 'Finance']
    selected_tab = request.GET.get('tab', departments[0])

    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
        csv_reader = csv.reader(decoded_file)
        next(csv_reader)  # skip header row

        for row in csv_reader:
            if not row or not row[1]:
                continue
            try:
                date_obj = datetime.strptime(row[1], "%Y-%m-%d").date()
            except ValueError:
                continue

            ReportData.objects.create(
                name=row[0],
                department=selected_tab,
                date=date_obj,
                data1=row[2] if len(row) > 2 else '',
                data2=row[3] if len(row) > 3 else '',
                data3=row[4] if len(row) > 4 else '',
            )

        messages.success(request, "CSV uploaded successfully.")
        return redirect(f'/my-reports/?tab={selected_tab}')

    # 🔍 Load report data based on selected tab
    reports = ReportData.objects.filter(department=selected_tab).order_by('-date')

    context = {
        'departments': departments,
        'selected_tab': selected_tab,
        'reports': reports,
    }
    return render(request, 'my_reports.html', context)

@login_required
def delete_report_view(request, report_id):
    report = get_object_or_404(ReportData, id=report_id)
    if request.method == 'POST':
        selected_tab = report.department
        report.delete()
        messages.success(request, "Report deleted successfully.")
        return redirect(f'/my-reports/?tab={selected_tab}')

def export_reports_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reports.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Name', 'Department', 'Date', 'Is Manual'])

    # Example data, real data fetch kar lena
    data = [
        [1, 'Report 1', 'Finance', '2025-06-01', True],
        [2, 'Report 2', 'Operations', '2025-06-02', False],
        [3, 'Report 3', 'Mech', '2025-06-03', True],
    ]

    for row in data:
        writer.writerow(row)

    return response


from io import TextIOWrapper
import csv

@login_required
def rail_madad_view(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = TextIOWrapper(csv_file.file, encoding='utf-8')
        csv_reader = csv.reader(decoded_file)
        next(csv_reader)  # Skip header

        for row in csv_reader:
            if not row or not row[0]:
                continue

            try:
                reg_date = datetime.strptime(row[1], "%Y-%m-%d").date()
                close_date = datetime.strptime(row[2], "%Y-%m-%d").date() if row[2] else None
            except Exception as e:
                continue

            RailMadadReport.objects.create(
                ref_no=row[0],
                registration_date=reg_date,
                closing_date=close_date,
                complaint_description=row[3],
                status=row[4],
            )

        messages.success(request, "CSV uploaded successfully.")
        return redirect('rail_madad')

    reports = RailMadadReport.objects.all()
    return render(request, 'raid_madad.html', {
        'reports': reports
    })

@login_required
def delete_railmadad_view(request, complaint_id):
    complaint = get_object_or_404(RailMadadReport, id=complaint_id)
    if request.method == 'POST':
        complaint.delete()
        messages.success(request, "Complaint deleted.")
    return redirect('rail_madad')


@login_required
def jabalpur_operations_view(request):
    operations = JabalpurOperation.objects.all()
    return render(request, 'jabalpur_operations.html', {'operations': operations})


def custom_logout(request):
    logout(request)
    request.session.flush()
    return redirect('login')


def jabalpur_operations(request):
    me_data = MeBasicEntry.objects.all().order_by('-id')
    stats_data = StatsMonthlyEntry.objects.all().order_by('-id')
    
    me_form = MeBasicForm()
    stats_form = StatsMonthlyForm()
    
    if request.method == 'POST':
        if 'me_submit' in request.POST:
            me_form = MeBasicForm(request.POST)
            if me_form.is_valid():
                me_form.save()
                if request.is_ajax():
                    return JsonResponse({'status': 'success', 'message': 'ME Basic data added successfully!'})
                messages.success(request, 'ME Basic data added successfully!')
                return redirect('jabalpur_operations')
            else:
                if request.is_ajax():
                    return JsonResponse({'status': 'error', 'errors': me_form.errors}, status=400)
        
        elif 'stats_submit' in request.POST:
            stats_form = StatsMonthlyForm(request.POST)
            if stats_form.is_valid():
                stats_form.save()
                if request.is_ajax():
                    return JsonResponse({'status': 'success', 'message': 'Monthly stats added successfully!'})
                messages.success(request, 'Monthly stats added successfully!')
                return redirect('jabalpur_operations')
            else:
                if request.is_ajax():
                    return JsonResponse({'status': 'error', 'errors': stats_form.errors}, status=400)
    
    return render(request, 'jabalpur_operations.html', {
        'me_data': me_data,
        'stats_data': stats_data,
        'me_form': me_form,
        'stats_form': stats_form,
    })

# @login_required
# def jabalpur_operations_view(request):
#     me_form = MeBasicForm()
#     stats_form = StatsMonthlyForm()

#     if request.method == 'POST':
#         if 'me_submit' in request.POST:
#             me_form = MeBasicForm(request.POST)
#             if me_form.is_valid():
#                 me_form.save()
#                 return redirect('jabalpur-operations')

#         elif 'stats_submit' in request.POST:
#             stats_form = StatsMonthlyForm(request.POST)
#             if stats_form.is_valid():
#                 stats_form.save()
#                 return redirect('jabalpur-operations')

#     me_data = MeBasicEntry.objects.all()
#     stats_data = StatsMonthlyEntry.objects.all()

#     return render(request, 'jabalpur_operations.html', {
#         'me_form': me_form,
#         'stats_form': stats_form,
#         'me_data': me_data,
#         'stats_data': stats_data
#     })