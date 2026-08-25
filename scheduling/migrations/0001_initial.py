# scheduling/migrations/0001_initial.py
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plate_number', models.CharField(max_length=20, unique=True, verbose_name='Bien so xe')),
                ('vehicle_type', models.CharField(
                    choices=[('limousine_29', 'Limousine 29 cho'), ('coach_35', 'Xe khach 35 cho')],
                    default='limousine_29', max_length=20, verbose_name='Loai xe')),
                ('capacity', models.PositiveIntegerField(default=29, verbose_name='So cho')),
                ('source', models.CharField(
                    choices=[('internal', 'Xe noi bo'), ('contract', 'Xe hop dong'), ('rental', 'Xe thue ngoai')],
                    default='internal', max_length=20, verbose_name='Nguon xe')),
                ('priority', models.PositiveIntegerField(default=1, verbose_name='Uu tien (1=cao nhat)')),
                ('is_active', models.BooleanField(default=True, verbose_name='Dang hoat dong')),
                ('notes', models.TextField(blank=True, verbose_name='Ghi chu')),
            ],
            options={
                'verbose_name': 'Xe',
                'verbose_name_plural': 'Danh sach xe',
                'ordering': ['priority', 'plate_number'],
            },
        ),
        migrations.CreateModel(
            name='Guide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100, verbose_name='Ho ten')),
                ('phone', models.CharField(blank=True, max_length=20, verbose_name='Dien thoai')),
                ('languages', models.JSONField(default=list, verbose_name='Ngon ngu')),
                ('source', models.CharField(
                    choices=[('internal', 'HDV noi bo'), ('freelance', 'HDV cong tac'), ('outsource', 'HDV thue ngoai')],
                    default='internal', max_length=20, verbose_name='Loai HDV')),
                ('priority', models.PositiveIntegerField(default=1, verbose_name='Uu tien (1=cao nhat)')),
                ('is_active', models.BooleanField(default=True, verbose_name='Dang hoat dong')),
                ('notes', models.TextField(blank=True, verbose_name='Ghi chu')),
            ],
            options={
                'verbose_name': 'Huong dan vien',
                'verbose_name_plural': 'Danh sach HDV',
                'ordering': ['priority', 'full_name'],
            },
        ),
        migrations.CreateModel(
            name='TourDeparture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_code', models.CharField(max_length=50, unique=True, verbose_name='Ma doan')),
                ('tour_name', models.CharField(max_length=200, verbose_name='Ten tour')),
                ('tour_code', models.CharField(max_length=50, verbose_name='Ma tour')),
                ('departure_date', models.DateField(verbose_name='Ngay khoi hanh')),
                ('return_date', models.DateField(verbose_name='Ngay ket thuc')),
                ('duration_days', models.PositiveIntegerField(verbose_name='So ngay')),
                ('pax', models.PositiveIntegerField(verbose_name='So khach')),
                ('language', models.CharField(default='zh', max_length=50, verbose_name='Ngon ngu')),
                ('tour_tier', models.CharField(
                    choices=[('standard', 'Standard'), ('premium', 'Premium')],
                    default='standard', max_length=20, verbose_name='Hang tour')),
                ('status', models.CharField(
                    choices=[('pending', 'Cho xep lich'), ('scheduled', 'Da xep lich'),
                             ('confirmed', 'Da xac nhan'), ('completed', 'Hoan thanh'), ('cancelled', 'Huy')],
                    default='pending', max_length=20, verbose_name='Trang thai')),
                ('notes', models.TextField(blank=True, verbose_name='Ghi chu')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Doan khoi hanh',
                'verbose_name_plural': 'Danh sach doan',
                'ordering': ['departure_date'],
            },
        ),
        migrations.CreateModel(
            name='ScheduleAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('departure', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='assignment',
                    to='scheduling.tourdeparture',
                    verbose_name='Doan')),
                ('vehicle', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='assignments',
                    to='scheduling.vehicle',
                    verbose_name='Xe')),
                ('guide', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='assignments',
                    to='scheduling.guide',
                    verbose_name='HDV')),
                ('is_vehicle_internal', models.BooleanField(default=True, verbose_name='Xe noi bo')),
                ('is_guide_internal', models.BooleanField(default=True, verbose_name='HDV noi bo')),
                ('optimizer_score', models.FloatField(blank=True, null=True, verbose_name='Diem toi uu')),
                ('assigned_by', models.CharField(default='optimizer', max_length=100, verbose_name='Xep boi')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Phan cong lich',
                'verbose_name_plural': 'Bang phan cong lich',
            },
        ),
    ]
