from django.db import models
from suppliers.models import Supplier
from datetime import timedelta

class Tour(models.Model):
    # --- 1. Các trạng thái ---
    DRAFT = 'DRAFT'
    CONFIRMED = 'CONF'
    CANCELLED = 'CAN'

    STATUS_CHOICES = [
        (DRAFT, 'Bản nháp (Draft)'),
        (CONFIRMED, 'Đã chốt (Confirmed)'),
        (CANCELLED, 'Đã hủy (Cancelled)'),
    ]

    # --- 2. Các phương thức tính giá ---
    METHOD_PROFIT = 'PROFIT'
    METHOD_PERCENT = 'PERCENT'

    PRICING_CHOICES = [
        (METHOD_PROFIT, 'Theo lợi nhuận cố định'),
        (METHOD_PERCENT, 'Theo % lợi nhuận'),
    ]

    # --- 3. Thông tin cơ bản & Hồ sơ đoàn ---
    title = models.CharField(max_length=255, verbose_name="Tên chương trình Tour")
    subtitle = models.CharField(max_length=255, blank=True, verbose_name="Chủ đề / Slogan tour (Phụ đề)")
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã Tour / Mã đoàn (Code/Group Code)")
    group_code = models.CharField(max_length=50, blank=True, verbose_name="Mã đoàn (团号)")
    tour_type = models.CharField(max_length=100, default="定制团", verbose_name="Tính chất đoàn (团体性质)")
    
    guest_count = models.IntegerField(default=1, verbose_name="Số lượng khách (Pax)")
    guest_detail = models.CharField(max_length=100, blank=True, verbose_name="Chi tiết số khách (VD: 12成人 + 01小孩)")
    room_count_desc = models.CharField(max_length=100, blank=True, verbose_name="Số lượng phòng (VD: 07 间 + 01 加床)")
    vehicle_info = models.CharField(max_length=100, default="29 座", verbose_name="Loại xe phục vụ (用车)")
    guide_info = models.CharField(max_length=100, default="中文导游", verbose_name="Thông tin HDV (导游)")
    leader_info = models.CharField(max_length=100, blank=True, verbose_name="Trưởng đoàn (领队)")
    
    start_date = models.DateField(verbose_name="Ngày khởi hành")
    end_date = models.DateField(null=True, blank=True, verbose_name="Ngày kết thúc")
    days = models.IntegerField(default=1, verbose_name="Số ngày")
    nights = models.IntegerField(default=0, verbose_name="Số đêm")

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=DRAFT, verbose_name="Trạng thái"
    )

    # --- 4. Thông tin báo giá (Quotation Metadata) ---
    quoter_name = models.CharField(max_length=100, default="JASON", verbose_name="Người báo giá (报价人)")
    quoter_phone = models.CharField(max_length=50, default="034. 2268. 576", verbose_name="SĐT Người báo giá (电话)")
    quote_date = models.DateField(null=True, blank=True, verbose_name="Ngày báo giá (报价日期)")
    valid_until = models.DateField(null=True, blank=True, verbose_name="Thời hạn báo giá (有效期限)")
    customer_name = models.CharField(max_length=150, blank=True, verbose_name="Khách hàng / Đại diện")
    customer_phone = models.CharField(max_length=50, blank=True, verbose_name="SĐT Khách hàng")
    
    flights_summary = models.TextField(
        blank=True, 
        verbose_name="Tóm tắt chuyến bay (班机)",
        help_text="VD: 27-07: CZ8315 CAN - HAN 1340 – 1445\n30-07: VN1345 HAN - CXR 1135 – 1325"
    )

    # --- 5. Nhập liệu tính giá & Tài chính báo giá ---
    currency = models.CharField(max_length=10, default="₫", verbose_name="Đơn vị tiền tệ")
    pricing_method = models.CharField(
        max_length=10, choices=PRICING_CHOICES, default=METHOD_PERCENT, verbose_name="Cách tính giá"
    )
    margin_amount = models.DecimalField(
        default=0, max_digits=12, decimal_places=0, verbose_name="Lợi nhuận mong muốn (VND)"
    )
    margin_percent = models.IntegerField(
        default=10, verbose_name="% Lợi nhuận"
    )
    deposit_amount = models.DecimalField(
        default=0, max_digits=12, decimal_places=0, verbose_name="Tiền đặt cọc báo giá (定金)"
    )
    custom_total_price = models.DecimalField(
        null=True, blank=True, max_digits=12, decimal_places=0, 
        verbose_name="Tổng giá cố định báo khách (Nếu nhập sẽ ưu tiên)"
    )

    # --- 6. Điều khoản & Tiêu chuẩn dịch vụ chi tiết (Brochure / Inclusions / Exclusions) ---
    hotel_standards = models.TextField(
        blank=True,
        verbose_name="Tiêu chuẩn khách sạn chi tiết (酒店标准)",
        help_text="Chi tiết phòng, loại phòng, số lượng, bữa ăn theo từng khách sạn"
    )
    inclusions = models.TextField(
        blank=True,
        verbose_name="Dịch vụ bao gồm trong Land tour (地接包含)",
        help_text="Xe, các bữa ăn, vé tham quan, thuyền buồm, HDV, nước suối, bảo hiểm..."
    )
    exclusions = models.TextField(
        blank=True,
        verbose_name="Chi phí không bao gồm (费用不含)",
        help_text="Visa, chi tiêu cá nhân, OT lái xe/HDV, phụ thu phòng đơn, trò chơi tự phí..."
    )
    tips = models.TextField(
        blank=True,
        verbose_name="Lưu ý thân thiện (温馨提示)",
        help_text="Hộ chiếu, thuốc men, trang phục, an toàn bơi lội..."
    )
    terms = models.TextField(
        blank=True,
        verbose_name="Quy định & Điều kiện đăng ký (报名须知)",
        help_text="Độ tuổi, quy định người cao tuổi, trẻ em, bệnh nền..."
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Ghi chú báo giá (备注说明)",
        help_text="Các điều khoản riêng trên bảng báo giá chi phí"
    )

    # --- 7. Thông tin đơn vị du lịch phát hành (Footer contact) ---
    company_name = models.CharField(max_length=150, default="新鸿泰旅游服务公司", verbose_name="Tên công ty")
    company_address = models.CharField(
        max_length=255, 
        default="306, VANH DAI TRONG, BINH TRI DONG B, BINH TAN, HCM", 
        verbose_name="Địa chỉ công ty"
    )
    company_landline = models.CharField(max_length=50, default="028-62654888", verbose_name="Điện thoại bàn")
    company_hotline = models.CharField(max_length=50, default="0923381385 阿昌", verbose_name="Hotline tư vấn")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.code}] {self.title}"

    # --- LOGIC TÍNH GIÁ (SALES & COSTING) ---
    @property
    def total_cost(self):
        """Tổng giá vốn (Net) thực tế của tất cả dịch vụ và nhà cung cấp"""
        total = 0
        for service in self.services.all():
            total += service.total_supplier_cost
        return total

    @property
    def calculated_selling_price(self):
        """Tổng giá bán (Sales) tính theo cost + margin hoặc cộng dồn các dịch vụ"""
        if self.pricing_method == self.METHOD_PROFIT and self.margin_amount > 0:
            return self.total_cost + self.margin_amount
        elif self.pricing_method == self.METHOD_PERCENT and self.margin_percent > 0:
            return self.total_cost + (self.total_cost * self.margin_percent / 100)
        else:
            total_s = sum(s.total_selling for s in self.services.all())
            return total_s if total_s > 0 else self.total_cost

    @property
    def total_price(self):
        """Tổng giá bán cuối cùng (Nếu có custom_total_price thì ưu tiên)"""
        if self.custom_total_price and self.custom_total_price > 0:
            return self.custom_total_price
        total_s = sum(s.total_selling for s in self.services.all())
        if total_s > 0:
            return total_s
        return self.calculated_selling_price

    @property
    def profit(self):
        return self.total_price - self.total_cost

    @property
    def price_per_pax(self):
        if self.guest_count > 0:
            return self.total_price / self.guest_count
        return 0

    @property
    def balance_receivable(self):
        """Số dư còn lại báo khách (Tổng giá - Đặt cọc)"""
        return max(0, self.total_price - self.deposit_amount)

    # ==========================================
    # LOGIC TÀI CHÍNH THỰC TẾ (FINANCE & CASHFLOW)
    # ==========================================
    @property
    def total_collected(self):
        """Tổng tiền ĐÃ THU thực tế từ khách"""
        total = 0
        for receipt in self.receipts.all():
            total += receipt.amount
        return total

    @property
    def remaining_receivable(self):
        """Công nợ khách hàng thực tế (Phải thu - Đã thu)"""
        return self.total_price - self.total_collected

    @property
    def total_paid(self):
        """Tổng tiền ĐÃ CHI cho nhà cung cấp"""
        total = 0
        for payment in self.payments.all():
            total += payment.amount
        return total

    @property
    def cashflow_profit(self):
        """Lợi nhuận thực tế (Tiền túi hiện tại: Thu - Chi)"""
        return self.total_collected - self.total_paid


# --- QUẢN LÝ NGÀY TRONG TOUR (HÀNH TRÌNH TỔNG QUÁT & CHI TIẾT) ---
class TourDay(models.Model):
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='tour_days')
    day_number = models.IntegerField(verbose_name="Ngày thứ (Day)")
    day_date_str = models.CharField(max_length=50, blank=True, verbose_name="Ngày hiển thị (VD: 07月27日 hoặc 27/07)")
    
    # Header / Tiêu đề ngày
    title = models.CharField(max_length=255, verbose_name="Tiêu đề ngày (VD: 下龙湾初印象 —— 悠然启程，夜市初探)")
    
    # Trường cho Bảng ma trận tổng quan (Matrix Itinerary)
    routing_flight = models.CharField(
        max_length=150, 
        blank=True, 
        verbose_name="Chặng di chuyển & Giờ bay (行程/航段)", 
        help_text="VD: 国内 07:20 ✈️ 河内 14:45 hoặc 下龙湾 🚗 河内"
    )
    morning_desc = models.CharField(max_length=255, blank=True, verbose_name="Hoạt động Sáng (上午)")
    afternoon_desc = models.CharField(max_length=255, blank=True, verbose_name="Hoạt động Chiều (下午)")
    evening_desc = models.CharField(max_length=255, blank=True, verbose_name="Hoạt động Tối (晚上)")
    
    # Bài thuyết minh chi tiết cho Brochure
    description = models.TextField(blank=True, verbose_name="Nội dung chi tiết ngày (Brochure Description)")
    
    # Khách sạn & Bữa ăn
    hotel_name = models.CharField(max_length=150, blank=True, verbose_name="Khách sạn lưu trú (住宿酒店)")
    meal_breakfast = models.CharField(max_length=50, default="酒店早餐", verbose_name="Bữa sáng (早餐)")
    meal_lunch = models.CharField(max_length=50, default="含", verbose_name="Bữa trưa (午餐)")
    meal_dinner = models.CharField(max_length=50, default="自理", verbose_name="Bữa tối (晚餐)")

    class Meta:
        ordering = ['day_number']

    def __str__(self):
        return f"Ngày {self.day_number}: {self.title}"


# --- QUẢN LÝ DỊCH VỤ & BẢNG CHI PHÍ TẠM TÍNH ---
class TourService(models.Model):
    CATEGORY_FLIGHT = 'FLIGHT'
    CATEGORY_HOTEL = 'HOTEL'
    CATEGORY_LANDTOUR = 'LANDTOUR'
    CATEGORY_TRANSPORT = 'TRANSPORT'
    CATEGORY_SIGHTSEEING = 'SIGHTSEEING'
    CATEGORY_RESTAURANT = 'RESTAURANT'
    CATEGORY_GUIDE = 'GUIDE'
    CATEGORY_INSURANCE = 'INSURANCE'
    CATEGORY_OTHER = 'OTHER'

    CATEGORY_CHOICES = [
        (CATEGORY_FLIGHT, '1. Vé máy bay (机票)'),
        (CATEGORY_HOTEL, '2. Khách sạn (酒店)'),
        (CATEGORY_LANDTOUR, '3. Land tour trọn gói (地接费)'),
        (CATEGORY_TRANSPORT, '4. Xe du lịch (用车)'),
        (CATEGORY_SIGHTSEEING, '5. Vé thắng cảnh (门票/缆车)'),
        (CATEGORY_RESTAURANT, '6. Nhà hàng / Ăn uống (餐饮)'),
        (CATEGORY_GUIDE, '7. Hướng dẫn viên (导游)'),
        (CATEGORY_INSURANCE, '8. Bảo hiểm du lịch (保险)'),
        (CATEGORY_OTHER, '9. Khác (其他)'),
    ]

    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='services')
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_HOTEL, verbose_name="Hạng mục dịch vụ"
    )
    service_name = models.CharField(max_length=255, verbose_name="Tên dịch vụ / Tiêu đề hạng mục (服务项目)")
    detail_content = models.TextField(blank=True, verbose_name="Nội dung cụ thể (具体内容)")
    
    # 1. Khách sạn (Check-in, Check-out & Số đêm)
    check_in = models.DateField(null=True, blank=True, verbose_name="Check-in / Ngày bắt đầu")
    check_out = models.DateField(null=True, blank=True, verbose_name="Check-out / Ngày kết thúc")
    quantity = models.IntegerField(default=1, verbose_name="Số lượng (数量/Phòng/Khách)")
    nights = models.IntegerField(default=1, verbose_name="Số đêm / Số lần (晚数/次数)")

    # 2. Giá Báo Khách (Customer Facing - Public)
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=0, default=0, null=True, blank=True, verbose_name="Đơn giá báo khách (单价)"
    )
    selling_total_price = models.DecimalField(
        null=True, blank=True, max_digits=12, decimal_places=0, verbose_name="Thành tiền báo khách (总价)"
    )

    # 3. Chi Phí Nhà Cung Cấp Đơn Lẻ (Supplier Cost - Internal / Confidential)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Nhà cung cấp trực tiếp")
    contract_unit_price = models.DecimalField(
        max_digits=12, decimal_places=0, default=0, null=True, blank=True, verbose_name="Giá hợp đồng NCC (合同价/Net)"
    )
    contract_total_price = models.DecimalField(
        null=True, blank=True, max_digits=12, decimal_places=0, verbose_name="Tổng chi phí NCC (总成本)"
    )

    # Các trường tương thích cũ (Aliases / Helpers)
    custom_total_price = models.DecimalField(
        null=True, blank=True, max_digits=12, decimal_places=0, verbose_name="Thành tiền tùy chỉnh"
    )
    price_net = models.DecimalField(
        max_digits=12, decimal_places=0, default=0, null=True, blank=True, verbose_name="Đơn giá Net"
    )
    service_date = models.DateField(null=True, blank=True, verbose_name="Ngày sử dụng")
    end_date = models.DateField(null=True, blank=True, verbose_name="Ngày kết thúc")

    note = models.TextField(blank=True, verbose_name="Ghi chú dịch vụ (备注)")
    order_index = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")

    class Meta:
        ordering = ['order_index', 'category', 'id']

    def save(self, *args, **kwargs):
        # 1. Tự động tính số đêm nếu có check-in và check-out
        if self.check_in and self.check_out:
            delta = (self.check_out - self.check_in).days
            self.nights = max(1, delta)
            self.service_date = self.check_in
            self.end_date = self.check_out
        elif self.service_date:
            self.check_in = self.service_date
            if self.end_date:
                self.check_out = self.end_date
                delta = (self.check_out - self.check_in).days
                self.nights = max(1, delta)

        if not self.quantity or self.quantity < 1:
            self.quantity = 1
        if not self.nights or self.nights < 1:
            self.nights = 1

        # 2. Tự động tính Thành tiền báo khách (selling_total_price)
        if self.unit_price and self.unit_price > 0:
            if self.selling_total_price is None or self.selling_total_price == 0:
                self.selling_total_price = int(self.quantity) * int(self.unit_price) * max(1, int(self.nights))
        elif self.selling_total_price and self.selling_total_price > 0 and (not self.unit_price or self.unit_price == 0):
            self.unit_price = self.selling_total_price // (self.quantity * max(1, self.nights))

        # Đồng bộ custom_total_price
        if self.selling_total_price and self.selling_total_price > 0:
            self.custom_total_price = self.selling_total_price
        elif self.custom_total_price and self.custom_total_price > 0:
            self.selling_total_price = self.custom_total_price

        # 3. Tự động tính Tổng chi phí NCC đơn lẻ (contract_total_price)
        if self.contract_unit_price and self.contract_unit_price > 0:
            if self.contract_total_price is None or self.contract_total_price == 0:
                self.contract_total_price = int(self.quantity) * int(self.contract_unit_price) * max(1, int(self.nights))
            self.price_net = self.contract_unit_price
        elif self.price_net and self.price_net > 0:
            self.contract_unit_price = self.price_net
            if self.contract_total_price is None or self.contract_total_price == 0:
                self.contract_total_price = int(self.quantity) * int(self.contract_unit_price) * max(1, int(self.nights))

        super().save(*args, **kwargs)

    @property
    def total_selling(self):
        """Thành tiền báo cho khách"""
        if self.selling_total_price and self.selling_total_price > 0:
            return self.selling_total_price
        if self.custom_total_price and self.custom_total_price > 0:
            return self.custom_total_price
        return (self.quantity or 1) * (self.unit_price or 0) * max(1, (self.nights or 1))

    @property
    def total_supplier_cost(self):
        """Tổng chi phí NCC (Nếu có các chi phí con đa NCC thì cộng dồn, ngược lại lấy contract_total_price)"""
        # Nếu có các khoản chi phí con từ nhiều NCC
        if self.sub_costs.exists():
            return sum(item.contract_total_price for item in self.sub_costs.all())
        if self.contract_total_price and self.contract_total_price > 0:
            return self.contract_total_price
        return (self.quantity or 1) * (self.contract_unit_price or self.price_net or 0) * max(1, (self.nights or 1))

    @property
    def total_net(self):
        return self.total_supplier_cost

    @property
    def total_amount(self):
        return self.total_selling

    @property
    def effective_unit_price(self):
        if self.unit_price is not None and self.unit_price > 0:
            return self.unit_price
        return 0

    @property
    def profit(self):
        """Lợi nhuận của từng dòng dịch vụ"""
        return self.total_selling - self.total_supplier_cost

    def __str__(self):
        return f"{self.service_name} ({self.get_category_display()})"


# --- QUẢN LÝ CHI PHÍ CON TỪ NHIỀU NHÀ CUNG CẤP (LANDTOUR SUB-COSTS) ---
class TourServiceCost(models.Model):
    service = models.ForeignKey(TourService, on_delete=models.CASCADE, related_name='sub_costs', verbose_name="Thuộc Dịch vụ / Landtour")
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Nhà cung cấp")
    cost_name = models.CharField(max_length=255, verbose_name="Khoản mục chi phí (VD: Thuê xe 29 chỗ, 6 bữa ăn, Cano 3 đảo...)")
    quantity = models.IntegerField(default=1, verbose_name="Số lượng")
    times = models.IntegerField(default=1, verbose_name="Số lần / Số ngày")
    contract_unit_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Đơn giá hợp đồng NCC (VND)")
    contract_total_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Tổng chi phí NCC (VND)")
    note = models.TextField(blank=True, verbose_name="Ghi chú")

    def save(self, *args, **kwargs):
        if not self.quantity or self.quantity < 1:
            self.quantity = 1
        if not self.times or self.times < 1:
            self.times = 1
        if self.contract_total_price is None or self.contract_total_price == 0:
            self.contract_total_price = int(self.quantity) * int(self.times) * int(self.contract_unit_price or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cost_name}: {self.contract_total_price:,.0f} VND"



