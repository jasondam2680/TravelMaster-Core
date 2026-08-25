from django.urls import path
from . import views

urlpatterns = [
    # Khi truy cập vào đường dẫn gốc của app, gọi hàm supplier_list
    path('', views.supplier_list, name='supplier_list'),

    # Thêm dòng này: <int:pk> nghĩa là "số nguyên ID" (Primary Key)
    path('<int:pk>/', views.supplier_detail, name='supplier_detail'),
]
