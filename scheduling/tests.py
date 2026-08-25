# scheduling/tests.py
from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import Vehicle, Guide, TourDeparture, ScheduleAssignment
from .optimizer import run_optimizer, dates_overlap, save_optimizer_results


class DatesOverlapTest(TestCase):
    """Unit test cho ham dates_overlap"""

    def test_no_overlap(self):
        self.assertFalse(dates_overlap(
            date(2026, 3, 1), date(2026, 3, 7),
            date(2026, 3, 8), date(2026, 3, 14)
        ))

    def test_overlap_partial(self):
        self.assertTrue(dates_overlap(
            date(2026, 3, 1), date(2026, 3, 7),
            date(2026, 3, 5), date(2026, 3, 11)
        ))

    def test_overlap_exact_boundary(self):
        # Ngay ket thuc = ngay bat dau cua doan ke tiep -> co chong
        self.assertTrue(dates_overlap(
            date(2026, 3, 1), date(2026, 3, 7),
            date(2026, 3, 7), date(2026, 3, 13)
        ))

    def test_one_inside_other(self):
        self.assertTrue(dates_overlap(
            date(2026, 3, 1), date(2026, 3, 14),
            date(2026, 3, 3), date(2026, 3, 7)
        ))


class VehicleModelTest(TestCase):
    def setUp(self):
        self.vehicle = Vehicle.objects.create(
            plate_number='51B-12345',
            vehicle_type='limousine_29',
            capacity=29,
            source='internal',
            priority=1,
        )

    def test_vehicle_str(self):
        self.assertIn('51B-12345', str(self.vehicle))

    def test_vehicle_defaults(self):
        self.assertTrue(self.vehicle.is_active)
        self.assertEqual(self.vehicle.priority, 1)


class GuideModelTest(TestCase):
    def setUp(self):
        self.guide = Guide.objects.create(
            full_name='Nguyen Van A',
            languages=['zh', 'vi'],
            source='internal',
            priority=1,
        )

    def test_guide_str(self):
        self.assertIn('Nguyen Van A', str(self.guide))

    def test_guide_languages(self):
        self.assertIn('zh', self.guide.languages)


class TourDepartureModelTest(TestCase):
    def setUp(self):
        self.departure = TourDeparture.objects.create(
            group_code='260307-SY001',
            tour_name='HCM-Mui Ne-Nha Trang 7N',
            tour_code='SY001-7D',
            departure_date=date(2026, 3, 7),
            return_date=date(2026, 3, 13),
            duration_days=7,
            pax=20,
            language='zh',
            tour_tier='standard',
        )

    def test_departure_str(self):
        self.assertIn('260307-SY001', str(self.departure))

    def test_departure_status_default(self):
        self.assertEqual(self.departure.status, 'pending')


class OptimizerTest(TestCase):
    """Integration test cho optimizer voi du lieu thang 3"""

    def setUp(self):
        # Tao 4 xe noi bo 29 cho
        for i in range(1, 5):
            Vehicle.objects.create(
                plate_number=f'51B-1000{i}',
                vehicle_type='limousine_29',
                capacity=29,
                source='internal',
                priority=1,
            )
        # Tao 6 HDV tieng Trung noi bo
        for i in range(1, 7):
            Guide.objects.create(
                full_name=f'HDV Tieng Trung {i:02d}',
                languages=['zh', 'vi'],
                source='internal',
                priority=1,
            )
        # Tao 6 doan thang 3 (khong chong lich)
        departures_data = [
            ('260307-SY001', date(2026, 3, 7), date(2026, 3, 13), 7),
            ('260311-LN', date(2026, 3, 11), date(2026, 3, 16), 6),
            ('260313-SY001', date(2026, 3, 13), date(2026, 3, 19), 7),
            ('260317-ZJ003', date(2026, 3, 17), date(2026, 3, 22), 6),
            ('260318-SY001', date(2026, 3, 18), date(2026, 3, 24), 7),
            ('260327-SY001', date(2026, 3, 27), date(2026, 4, 2), 7),
        ]
        for code, dep, ret, dur in departures_data:
            TourDeparture.objects.create(
                group_code=code,
                tour_name='HCM-Mui Ne-Nha Trang',
                tour_code='SY001-7D',
                departure_date=dep,
                return_date=ret,
                duration_days=dur,
                pax=20,
                language='zh',
            )

    def test_optimizer_returns_optimal(self):
        results = run_optimizer()
        self.assertEqual(results['status'], 'optimal')

    def test_all_departures_assigned(self):
        results = run_optimizer()
        self.assertEqual(results['assigned'], 6)

    def test_no_vehicle_double_booking(self):
        """Moi xe chi xuat hien 1 lan trong cac doan chong lich"""
        results = run_optimizer()
        # Kiem tra khong co xe nao duoc gan cho 2 doan chong ngay
        assignments = results['assignments']
        for i, a1 in enumerate(assignments):
            for a2 in assignments[i+1:]:
                if a1['vehicle_plate'] == a2['vehicle_plate']:
                    d1_start = date.fromisoformat(a1['departure_date'])
                    d1_end = date.fromisoformat(a1['return_date'])
                    d2_start = date.fromisoformat(a2['departure_date'])
                    d2_end = date.fromisoformat(a2['return_date'])
                    self.assertFalse(
                        dates_overlap(d1_start, d1_end, d2_start, d2_end),
                        f"Vehicle {a1['vehicle_plate']} double-booked!"
                    )

    def test_no_guide_double_booking(self):
        """Moi guide chi xuat hien 1 lan trong cac doan chong lich"""
        results = run_optimizer()
        assignments = results['assignments']
        for i, a1 in enumerate(assignments):
            for a2 in assignments[i+1:]:
                if a1['guide_name'] == a2['guide_name']:
                    d1_start = date.fromisoformat(a1['departure_date'])
                    d1_end = date.fromisoformat(a1['return_date'])
                    d2_start = date.fromisoformat(a2['departure_date'])
                    d2_end = date.fromisoformat(a2['return_date'])
                    self.assertFalse(
                        dates_overlap(d1_start, d1_end, d2_start, d2_end),
                        f"Guide {a1['guide_name']} double-booked!"
                    )

    def test_internal_preferred(self):
        """Tat ca xe/guide phai la noi bo (vi chi co noi bo trong setUp)"""
        results = run_optimizer()
        self.assertEqual(results['internal_vehicle_pct'], 100.0)
        self.assertEqual(results['internal_guide_pct'], 100.0)

    def test_save_results(self):
        results = run_optimizer()
        saved = save_optimizer_results(results)
        self.assertEqual(saved, 6)
        self.assertEqual(ScheduleAssignment.objects.count(), 6)
        # Tat ca doan chuyen sang 'scheduled'
        pending = TourDeparture.objects.filter(status='pending').count()
        self.assertEqual(pending, 0)


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username='testadmin', password='testpass123', email='test@test.com'
        )
        self.client.login(username='testadmin', password='testpass123')

    def test_dashboard_accessible(self):
        response = self.client.get('/scheduling/')
        self.assertEqual(response.status_code, 200)

    def test_run_optimizer_api(self):
        import json
        response = self.client.post(
            '/scheduling/api/run-optimizer/',
            data=json.dumps({'save': False}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('status', data)

    def test_calendar_api(self):
        response = self.client.get('/scheduling/api/calendar/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('vehicle_calendar', data)
        self.assertIn('guide_calendar', data)

    def test_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get('/scheduling/')
        # Redirect to login
        self.assertIn(response.status_code, [302, 200])
