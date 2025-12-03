from django.urls import path
from . import views

urlpatterns = [
    # Đường dẫn gốc của app tours: Hiển thị danh sách
    path('', views.tour_list, name='tour_list'),

    # Đường dẫn ví dụ: /tours/1/
    path('<int:pk>/', views.tour_detail, name='tour_detail'),

    # Đường dẫn mới cho trang Báo giá khách
    path('<int:pk>/print/', views.tour_quotation, name='tour_quotation'),

    path('<int:tour_id>/booking/<int:supplier_id>/', views.booking_order, name='booking_order'),
]
