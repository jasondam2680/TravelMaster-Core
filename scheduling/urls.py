# scheduling/urls.py
from django.urls import path
from . import views

app_name = 'scheduling'

urlpatterns = [
    # Dashboard
    path('', views.schedule_dashboard, name='dashboard'),

    # Calendar month view
    path('calendar/', views.calendar_view, name='calendar'),

    # Optimizer
    path('run-optimizer/', views.run_schedule_optimizer, name='run_optimizer'),
    path('results/', views.get_optimizer_results, name='results'),

    # Export endpoints
    path('export/schedule/', views.export_schedule_csv, name='export_schedule'),
    path('export/vehicle-calendar/', views.export_vehicle_calendar, name='export_vehicle_calendar'),
    path('export/guide-calendar/', views.export_guide_calendar, name='export_guide_calendar'),

    # API endpoints
    path('api/run-optimizer/', views.run_schedule_optimizer, name='run_optimizer_api'),
    path('api/calendar/', views.get_schedule_calendar, name='calendar_api'),
    path('api/tour-detail/<str:tour_code>/', views.tour_detail_api, name='tour_detail_api'),
]
