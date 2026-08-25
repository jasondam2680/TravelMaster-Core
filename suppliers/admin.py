from django.contrib import admin
from .models import Supplier # Nhập cái bản vẽ Supplier vào đây

# Đăng ký model Supplier với trang Admin
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    # Quy định những cột nào sẽ hiện ra ở danh sách chung
    list_display = ('name', 'type', 'agent_contact', 'payment_term')

    # Tạo thanh tìm kiếm theo tên và SĐT
    search_fields = ('name', 'agent_contact', 'landline')

    # Tạo bộ lọc bên tay phải (lọc theo loại hình và thanh toán)
    list_filter = ('type', 'payment_term')
