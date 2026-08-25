from django.urls import path
from . import views

urlpatterns = [
    # Danh sách Tour (Dashboard)
    path('', views.tour_list, name='tour_list'),

    # Chi tiết Tour (Nội bộ điều hành)
    path('<int:pk>/', views.tour_detail, name='tour_detail'),

    # --- WORKFLOW BÁO GIÁ 4 BƯỚC ---
    # Bước 1: Hành trình tổng quát (Ma trận)
    path('<int:pk>/matrix/', views.quote_matrix_overview, name='quote_matrix_overview'),
    
    # Bước 2: Bảng chi phí tạm tính (Costing Sheet)
    path('<int:pk>/costing/', views.quote_costing_sheet, name='quote_costing_sheet'),
    
    # Bước 3 & 4: Báo giá Tour chi tiết & Xuất Brochure
    path('<int:pk>/proposal/', views.quote_proposal_brochure, name='quote_proposal_brochure'),

    # Tương thích đường dẫn cũ
    path('<int:pk>/print/', views.tour_quotation, name='tour_quotation'),

    # Booking Order cho nhà cung cấp
    path('<int:tour_id>/booking/<int:supplier_id>/', views.booking_order, name='booking_order'),
]

