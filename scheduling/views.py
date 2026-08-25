# scheduling/views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View
import json
import csv
from datetime import datetime, timedelta
from calendar import monthcalendar, month_name as cal_month_name

from .models import TourDeparture, Vehicle, Guide, ScheduleAssignment
from .optimizer import run_optimizer, save_optimizer_results


@staff_member_required
def schedule_dashboard(request):
    """Trang tong quan lich xe/guide"""
    departures = TourDeparture.objects.all().order_by('departure_date')
    assignments = ScheduleAssignment.objects.select_related(
        'departure', 'vehicle', 'guide'
    ).order_by('departure__departure_date')

    context = {
        'departures': departures,
        'assignments': assignments,
        'pending_count': departures.filter(status='pending').count(),
        'scheduled_count': departures.filter(status='scheduled').count(),
    }
    return render(request, 'scheduling/dashboard.html', context)


@staff_member_required
@require_POST
def run_schedule_optimizer(request):
    """API: Chay optimizer va tra ve ket qua JSON"""
    try:
        body = json.loads(request.body) if request.body else {}
        save = body.get('save', False)
        results = run_optimizer()
        if save and results.get('status') == 'optimal':
            saved_count = save_optimizer_results(results)
            results['saved_count'] = saved_count
        return JsonResponse(results, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@staff_member_required
@require_GET
def get_schedule_calendar(request):
    """API: Tra ve lich theo dinh dang calendar cho xe va guide"""
    assignments = ScheduleAssignment.objects.select_related(
        'departure', 'vehicle', 'guide'
    ).order_by('departure__departure_date')

    vehicle_calendar = {}
    guide_calendar = {}

    for a in assignments:
        d = a.departure
        # Vehicle calendar
        plate = a.vehicle.plate_number
        if plate not in vehicle_calendar:
            vehicle_calendar[plate] = []
        vehicle_calendar[plate].append({
            'group_code': d.group_code,
            'tour_name': d.tour_name,
            'departure_date': str(d.departure_date),
            'return_date': str(d.return_date),
            'pax': d.pax,
            'guide': a.guide.full_name,
        })
        # Guide calendar
        guide_name = a.guide.full_name
        if guide_name not in guide_calendar:
            guide_calendar[guide_name] = []
        guide_calendar[guide_name].append({
            'group_code': d.group_code,
            'tour_name': d.tour_name,
            'departure_date': str(d.departure_date),
            'return_date': str(d.return_date),
            'pax': d.pax,
            'vehicle': a.vehicle.plate_number,
        })

    return JsonResponse({
        'vehicle_calendar': vehicle_calendar,
        'guide_calendar': guide_calendar,
        'total_assignments': assignments.count(),
    })


@staff_member_required
def get_optimizer_results(request):
    """Hien thi ket qua toi uu hoa gan nhat"""
    assignments = ScheduleAssignment.objects.select_related(
        'departure', 'vehicle', 'guide'
    ).order_by('departure__departure_date')
    context = {
        'assignments': assignments,
        'total': assignments.count(),
    }
    return render(request, 'scheduling/optimizer_results.html', context)


# Calendar View
@staff_member_required
def calendar_view(request):
    """Display monthly calendar view with tour assignments"""
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))

    # Generate calendar days
    cal = monthcalendar(year, month)

    calendar_days = []
    for week in cal:
        for day in week:
            if day == 0:
                continue
            date = datetime(year, month, day)

            # Get tours for this day
            events_list = []
            all_tours = TourDeparture.objects.all()

            for tour in all_tours:
                tour_end = tour.departure_date + timedelta(days=tour.duration_days - 1)
                if tour.departure_date <= date.date() <= tour_end:
                    assignment = ScheduleAssignment.objects.filter(departure=tour).first()
                    events_list.append({
                        'tour_id': tour.id,
                        'group_code': tour.group_code,
                        'tour_code': tour.tour_code,
                        'pax': tour.pax,
                        'is_start_day': tour.departure_date == date.date(),
                        'vehicle': assignment.vehicle.plate_number if assignment and assignment.vehicle else '',
                        'guide': assignment.guide.full_name if assignment and assignment.guide else ''
                    })

            calendar_days.append({
                'date': date,
                'day': day,
                'is_today': date.date() == datetime.now().date(),
                'is_weekend': date.weekday() >= 5,
                'is_other_month': False,
                'events': events_list
            })

    # Stats for the month
    tours_this_month = TourDeparture.objects.filter(
        departure_date__year=year,
        departure_date__month=month
    )
    active_assignments = ScheduleAssignment.objects.filter(
        departure__departure_date__year=year,
        departure__departure_date__month=month
    )
    unique_vehicles = active_assignments.values('vehicle').distinct().count()
    unique_guides = active_assignments.values('guide').distinct().count()
    total_vehicles = Vehicle.objects.filter(is_active=True).count()
    occupancy = round((unique_vehicles / max(total_vehicles, 1)) * 100, 1) if total_vehicles > 0 else 0

    context = {
        'calendar_days': calendar_days,
        'current_month': f"{cal_month_name[month]} {year}",
        'year': year,
        'month': month,
        'vehicles': Vehicle.objects.filter(is_active=True),
        'guides': Guide.objects.filter(is_active=True),
        'stats': {
            'total_tours': tours_this_month.count(),
            'active_vehicles': unique_vehicles,
            'active_guides': unique_guides,
            'occupancy_rate': occupancy
        }
    }

    return render(request, 'scheduling/calendar_view.html', context)


# Export functions
@staff_member_required
def export_schedule_csv(request):
    """Xuat lich phan cong ra CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="schedule_export.csv"'
    response.write('\ufeff')  # BOM for Excel

    writer = csv.writer(response)
    writer.writerow(['Ma doan', 'Ten tour', 'Ma tour', 'Ngay di', 'Ngay ve', 'So ngay', 'So khach', 'Hang tour', 'Bien so xe', 'HDV', 'Trang thai'])

    assignments = ScheduleAssignment.objects.select_related(
        'departure', 'vehicle', 'guide'
    ).order_by('departure__departure_date')

    for a in assignments:
        d = a.departure
        writer.writerow([
            d.group_code,
            d.tour_name,
            d.tour_code,
            d.departure_date.strftime('%d/%m/%Y'),
            d.return_date.strftime('%d/%m/%Y'),
            d.duration_days,
            d.pax,
            d.get_tour_tier_display(),
            a.vehicle.plate_number,
            a.guide.full_name,
            d.get_status_display(),
        ])

    # Also include unassigned departures
    unassigned = TourDeparture.objects.filter(assignment__isnull=True).order_by('departure_date')
    for d in unassigned:
        writer.writerow([
            d.group_code,
            d.tour_name,
            d.tour_code,
            d.departure_date.strftime('%d/%m/%Y'),
            d.return_date.strftime('%d/%m/%Y'),
            d.duration_days,
            d.pax,
            d.get_tour_tier_display(),
            'CHUA XEP',
            'CHUA XEP',
            d.get_status_display(),
        ])

    return response


@staff_member_required
def export_vehicle_calendar(request):
    """Xuat lich xe ra CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="vehicle_calendar.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Bien so xe', 'Loai xe', 'Ma doan', 'Ten tour', 'Ngay di', 'Ngay ve', 'So khach', 'HDV'])

    for vehicle in Vehicle.objects.filter(is_active=True).order_by('priority', 'plate_number'):
        for a in ScheduleAssignment.objects.filter(vehicle=vehicle).select_related('departure', 'guide').order_by('departure__departure_date'):
            d = a.departure
            writer.writerow([
                vehicle.plate_number,
                vehicle.get_vehicle_type_display(),
                d.group_code,
                d.tour_name,
                d.departure_date.strftime('%d/%m/%Y'),
                d.return_date.strftime('%d/%m/%Y'),
                d.pax,
                a.guide.full_name,
            ])

    return response


@staff_member_required
def export_guide_calendar(request):
    """Xuat lich HDV ra CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="guide_calendar.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Ho ten HDV', 'Ngon ngu', 'Ma doan', 'Ten tour', 'Ngay di', 'Ngay ve', 'So khach', 'Bien so xe'])

    for guide in Guide.objects.filter(is_active=True).order_by('priority', 'full_name'):
        for a in ScheduleAssignment.objects.filter(guide=guide).select_related('departure', 'vehicle').order_by('departure__departure_date'):
            d = a.departure
            writer.writerow([
                guide.full_name,
                ', '.join(guide.languages),
                d.group_code,
                d.tour_name,
                d.departure_date.strftime('%d/%m/%Y'),
                d.return_date.strftime('%d/%m/%Y'),
                d.pax,
                a.vehicle.plate_number,
            ])

    return response


# API endpoint for tour detail tooltip
@require_GET
def tour_detail_api(request, tour_code):
    """API endpoint to get tour details for tooltip"""
    try:
        tour = TourDeparture.objects.get(tour_code=tour_code)
        assignment = ScheduleAssignment.objects.filter(departure=tour).first()

        tour_end = tour.departure_date + timedelta(days=tour.duration_days - 1)

        data = {
            'group_code': tour.group_code,
            'tour_code': tour.tour_code,
            'tour_name': tour.tour_name,
            'departure_date': tour.departure_date.strftime('%d/%m/%Y'),
            'return_date': tour_end.strftime('%d/%m/%Y'),
            'duration': tour.duration_days,
            'pax': tour.pax,
            'tour_tier': tour.get_tour_tier_display(),
            'language': tour.language,
            'status': tour.get_status_display(),
            'vehicle': assignment.vehicle.plate_number if assignment and assignment.vehicle else None,
            'guide': assignment.guide.full_name if assignment and assignment.guide else None
        }

        return JsonResponse(data)
    except TourDeparture.DoesNotExist:
        return JsonResponse({'error': 'Tour not found'}, status=404)
