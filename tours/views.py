from django.shortcuts import render, get_object_or_404
from .models import Tour
from suppliers.models import Supplier

# 1. Trang danh sách Tour (Dashboard)
def tour_list(request):
    tours = Tour.objects.all().order_by('-created_at')
    context = {'tours': tours}
    return render(request, 'tours/list.html', context)

# 2. Trang chi tiết Tour (Nội bộ) - SỬA LỖI TẠI ĐÂY
def tour_detail(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    # Sắp xếp theo ngày sử dụng (service_date) thay vì day_number
    services = tour.services.all().order_by('service_date')

    context = {
        'tour': tour,
        'services': services
    }
    return render(request, 'tours/detail.html', context)

# 3. Trang Báo giá cho Khách (PDF)
def tour_quotation(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    services = tour.services.all().order_by('service_date')
    context = {
        'tour': tour,
        'services': services,
        'company_name': 'TRAVEL MASTER VIETNAM',
        'company_phone': '0909 123 456',
        'company_email': 'booking@travelmaster.vn',
    }
    return render(request, 'tours/quotation.html', context)

# 4. Trang tạo Booking Order
def booking_order(request, tour_id, supplier_id):
    tour = get_object_or_404(Tour, pk=tour_id)
    supplier = get_object_or_404(Supplier, pk=supplier_id)
    services = tour.services.filter(supplier=supplier).order_by('service_date')

    if supplier.type == 'HTL':
        template_name = 'tours/booking_hotel.html'
    elif supplier.type == 'TRP':
        template_name = 'tours/booking_transport.html'
    elif supplier.type == 'RES':
        template_name = 'tours/booking_restaurant.html'
    else:
        template_name = 'tours/booking_default.html'

    context = {
        'tour': tour,
        'supplier': supplier,
        'services': services,
        'my_company': {
            'name': 'TRAVEL MASTER VIETNAM',
            'email': 'booking@travelmaster.vn',
            'phone': '0909 123 456'
        }
    }
    return render(request, template_name, context)
