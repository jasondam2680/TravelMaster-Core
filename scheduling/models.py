# scheduling/models.py
from django.db import models


class Vehicle(models.Model):
    """Quản lý xe"""
    VEHICLE_TYPE_CHOICES = [
        ('limousine_29', 'Limousine 29 chỗ'),
        ('coach_35', 'Xe khách 35 chỗ'),
    ]
    SOURCE_CHOICES = [
        ('internal', 'Xe nội bộ'),
        ('contract', 'Xe hợp đồng'),
        ('rental', 'Xe thuê ngoài'),
    ]

    plate_number = models.CharField(max_length=20, unique=True, verbose_name='Biển số xe')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default='limousine_29', verbose_name='Loại xe')
    capacity = models.PositiveIntegerField(default=29, verbose_name='Số chỗ')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='internal', verbose_name='Nguồn xe')
    priority = models.PositiveIntegerField(default=1, verbose_name='Ưu tiên (1=cao nhất)')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    notes = models.TextField(blank=True, verbose_name='Ghi chú')

    class Meta:
        verbose_name = 'Xe'
        verbose_name_plural = 'Danh sách xe'
        ordering = ['priority', 'plate_number']

    def __str__(self):
        return f'{self.plate_number} ({self.get_vehicle_type_display()})'


class Guide(models.Model):
    """Quản lý hướng dẫn viên"""
    SOURCE_CHOICES = [
        ('internal', 'HDV nội bộ'),
        ('freelance', 'HDV cộng tác'),
        ('outsource', 'HDV thuê ngoài'),
    ]

    full_name = models.CharField(max_length=100, verbose_name='Họ tên')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Điện thoại')
    languages = models.JSONField(default=list, verbose_name='Ngôn ngữ')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='internal', verbose_name='Loại HDV')
    priority = models.PositiveIntegerField(default=1, verbose_name='Ưu tiên (1=cao nhất)')
    is_active = models.BooleanField(default=True, verbose_name='Đang hoạt động')
    notes = models.TextField(blank=True, verbose_name='Ghi chú')

    class Meta:
        verbose_name = 'Hướng dẫn viên'
        verbose_name_plural = 'Danh sách HDV'
        ordering = ['priority', 'full_name']

    def __str__(self):
        return f'{self.full_name} ({", ".join(self.languages)})'


class TourDeparture(models.Model):
    """Lịch khởi hành từng đoàn"""
    STATUS_CHOICES = [
        ('pending', 'Chờ xếp lịch'),
        ('scheduled', 'Đã xếp lịch'),
        ('confirmed', 'Đã xác nhận'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Huỷ'),
    ]
    TIER_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]

    group_code = models.CharField(max_length=50, unique=True, verbose_name='Mã đoàn')
    tour_name = models.CharField(max_length=200, verbose_name='Tên tour')
    tour_code = models.CharField(max_length=50, verbose_name='Mã tour')
    departure_date = models.DateField(verbose_name='Ngày khởi hành')
    return_date = models.DateField(verbose_name='Ngày kết thúc')
    duration_days = models.PositiveIntegerField(verbose_name='Số ngày')
    pax = models.PositiveIntegerField(verbose_name='Số khách')
    language = models.CharField(max_length=50, default='zh', verbose_name='Ngôn ngữ')
    tour_tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='standard', verbose_name='Hạng tour')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Trạng thái')
    notes = models.TextField(blank=True, verbose_name='Ghi chú')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Đoàn khởi hành'
        verbose_name_plural = 'Danh sách đoàn'
        ordering = ['departure_date']

    def __str__(self):
        return f'{self.group_code} | {self.departure_date} → {self.return_date} ({self.pax} pax)'


class ScheduleAssignment(models.Model):
    """Phân công xe + HDV cho từng đoàn"""
    departure = models.OneToOneField(TourDeparture, on_delete=models.CASCADE, related_name='assignment', verbose_name='Đoàn')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name='assignments', verbose_name='Xe')
    guide = models.ForeignKey(Guide, on_delete=models.PROTECT, related_name='assignments', verbose_name='HDV')
    is_vehicle_internal = models.BooleanField(default=True, verbose_name='Xe nội bộ')
    is_guide_internal = models.BooleanField(default=True, verbose_name='HDV nội bộ')
    optimizer_score = models.FloatField(null=True, blank=True, verbose_name='Điểm tối ưu')
    assigned_by = models.CharField(max_length=100, default='optimizer', verbose_name='Xếp bởi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Phân công lịch'
        verbose_name_plural = 'Bảng phân công lịch'

    def __str__(self):
        return f'{self.departure.group_code} → Xe: {self.vehicle} | HDV: {self.guide}'
