from django.db import models
from tours.models import Tour
from suppliers.models import Supplier

class Receipt(models.Model):
    """PHIẾU THU (Tiền khách trả)"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='receipts', verbose_name="Thuộc Tour")
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Số tiền thu (VND)")
    date = models.DateField(verbose_name="Ngày thu")
    payer = models.CharField(max_length=100, default="Khách hàng", verbose_name="Người nộp tiền")
    note = models.TextField(blank=True, verbose_name="Ghi chú (CK/Tiền mặt)")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Thu {self.amount:,.0f} - {self.tour.code}"

class Payment(models.Model):
    """PHIẾU CHI (Trả tiền NCC)"""
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='payments', verbose_name="Chi cho Tour")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, verbose_name="Chi cho NCC")
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Số tiền chi (VND)")
    date = models.DateField(verbose_name="Ngày chi")
    note = models.TextField(blank=True, verbose_name="Ghi chú (Cọc/Thanh toán hết)")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chi {self.amount:,.0f} - {self.supplier.name if self.supplier else 'Khác'}"

# Create your models here.
