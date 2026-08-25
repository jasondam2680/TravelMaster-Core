from django.shortcuts import render, get_object_or_404
from .models import Tour
from suppliers.models import Supplier

def _clean_lines(text):
    """Tách đoạn text nhiều dòng thành list các dòng sạch sẽ."""
    if not text:
        return []
    lines = []
    for line in text.strip().split('\n'):
        cleaned = line.strip()
        if cleaned:
            # Loại bỏ bullet đầu dòng nếu có để template render thẻ <li> chuẩn
            if cleaned.startswith('•') or cleaned.startswith('-') or cleaned.startswith('*'):
                cleaned = cleaned[1:].strip()
            lines.append(cleaned)
    return lines

# 1. Trang danh sách Tour (Dashboard)
def tour_list(request):
    tours = Tour.objects.all().order_by('-created_at')
    context = {'tours': tours}
    return render(request, 'tours/list.html', context)

# 2. Trang chi tiết Tour (Nội bộ & Điều hành)
def tour_detail(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    services = tour.services.all().order_by('order_index', 'category', 'id')
    tour_days = tour.tour_days.all().order_by('day_number')

    context = {
        'tour': tour,
        'services': services,
        'tour_days': tour_days,
    }
    return render(request, 'tours/detail.html', context)

# =========================================================================
# 3. WORKFLOW BÁO GIÁ 4 BƯỚC (QUOTATION WORKFLOW VIEWS)
# =========================================================================

# Bước 1: Hành trình tổng quát (Matrix Overview Itinerary - Mẫu Form 3)
def quote_matrix_overview(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    tour_days = tour.tour_days.all().order_by('day_number')
    
    context = {
        'tour': tour,
        'tour_days': tour_days,
    }
    return render(request, 'tours/quote_matrix_overview.html', context)

# Bước 2: Bảng chi phí tạm tính (Costing Breakdown Sheet - Mẫu Form 1)
def quote_costing_sheet(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    services = tour.services.all().order_by('order_index', 'category', 'id')
    
    # Chuẩn bị danh sách ghi chú
    note_lines = _clean_lines(tour.notes)
    
    context = {
        'tour': tour,
        'services': services,
        'note_lines': note_lines,
    }
    return render(request, 'tours/quote_costing_sheet.html', context)

# Bước 3 & 4: Báo giá Tour chi tiết & Xuất Brochure (Proposal Brochure - Mẫu Form 2)
def quote_proposal_brochure(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    tour_days = tour.tour_days.all().order_by('day_number')
    
    # Parse các đoạn text điều khoản thành bullet lists
    flights_list = _clean_lines(tour.flights_summary)
    hotel_standards_list = _clean_lines(tour.hotel_standards)
    inclusions_list = _clean_lines(tour.inclusions)
    exclusions_list = _clean_lines(tour.exclusions)
    tips_list = _clean_lines(tour.tips)
    terms_list = _clean_lines(tour.terms)
    
    context = {
        'tour': tour,
        'tour_days': tour_days,
        'flights_list': flights_list,
        'hotel_standards_list': hotel_standards_list,
        'inclusions_list': inclusions_list,
        'exclusions_list': exclusions_list,
        'tips_list': tips_list,
        'terms_list': terms_list,
    }
    return render(request, 'tours/quote_proposal_brochure.html', context)

# Trang Báo giá cũ (backward compatibility)
def tour_quotation(request, pk):
    return quote_costing_sheet(request, pk)

# Trang tạo Booking Order cho NCC
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
            'name': tour.company_name or '新鸿泰旅游服务公司',
            'phone': tour.company_hotline or '0923381385',
        }
    }
    return render(request, template_name, context)

