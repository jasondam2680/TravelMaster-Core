# scheduling/admin.py
from django.contrib import admin
from .models import Vehicle, Guide, TourDeparture, ScheduleAssignment


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['plate_number', 'vehicle_type', 'capacity', 'source', 'priority', 'is_active']
    list_filter = ['vehicle_type', 'source', 'is_active']
    search_fields = ['plate_number']
    ordering = ['priority', 'plate_number']


@admin.register(Guide)
class GuideAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'languages', 'source', 'priority', 'is_active']
    list_filter = ['source', 'is_active']
    search_fields = ['full_name', 'phone']
    ordering = ['priority', 'full_name']


@admin.register(TourDeparture)
class TourDepartureAdmin(admin.ModelAdmin):
    list_display = ['group_code', 'tour_name', 'departure_date', 'return_date', 'pax', 'tour_tier', 'status']
    list_filter = ['status', 'tour_tier', 'language']
    search_fields = ['group_code', 'tour_name', 'tour_code']
    ordering = ['departure_date']
    date_hierarchy = 'departure_date'


@admin.register(ScheduleAssignment)
class ScheduleAssignmentAdmin(admin.ModelAdmin):
    list_display = [
        'get_group_code', 'get_departure_date', 'get_return_date',
        'vehicle', 'guide', 'is_vehicle_internal', 'is_guide_internal', 'assigned_by'
    ]
    list_filter = ['is_vehicle_internal', 'is_guide_internal', 'assigned_by']
    search_fields = ['departure__group_code', 'vehicle__plate_number', 'guide__full_name']
    select_related = True

    def get_group_code(self, obj):
        return obj.departure.group_code
    get_group_code.short_description = 'Ma doan'

    def get_departure_date(self, obj):
        return obj.departure.departure_date
    get_departure_date.short_description = 'Ngay di'

    def get_return_date(self, obj):
        return obj.departure.return_date
    get_return_date.short_description = 'Ngay ve'
