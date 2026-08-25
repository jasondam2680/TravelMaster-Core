from django.shortcuts import render, get_object_or_404

# Create your views here.
from .models import Supplier

def supplier_list(request):
    # 1. Vào kho lấy toàn bộ danh sách nhà cung cấp
    all_suppliers = Supplier.objects.all()

    # 2. Gói ghém dữ liệu để gửi sang giao diện (Template)
    context = {
        'suppliers': all_suppliers
    }

    # 3. Trả về trang web (file html)
    return render(request, 'suppliers/list.html', context)
# --- Thêm hàm mới này vào dưới cùng ---
def supplier_detail(request, pk):
    # Tìm nhà cung cấp có id = pk, nếu không có thì trả về lỗi 404
    supplier = get_object_or_404(Supplier, pk=pk)

    context = {'supplier': supplier}
    return render(request, 'suppliers/detail.html', context)
