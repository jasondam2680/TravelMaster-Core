/**
 * Auto-calculation script for Tour Services & Hotel Dates in Django Admin
 * - Auto-calculates Nights from Check-in and Check-out
 * - Auto-calculates Selling Total = Quantity * Nights * Unit Price
 * - Auto-calculates Supplier Total = Quantity * Nights * Contract Unit Price
 * - Auto-calculates Sub-costs in Landtour = Quantity * Times * Contract Unit Price
 */
document.addEventListener('DOMContentLoaded', function() {
    function calculateRow(row) {
        if (!row) return;

        // 1. Calculate Nights from Check-in & Check-out
        const checkInInput = row.querySelector('input[name$="-check_in"]') || row.querySelector('input[name$="-service_date"]');
        const checkOutInput = row.querySelector('input[name$="-check_out"]') || row.querySelector('input[name$="-end_date"]');
        const nightsInput = row.querySelector('input[name$="-nights"]');
        const timesInput = row.querySelector('input[name$="-times"]');

        if (checkInInput && checkOutInput && nightsInput && checkInInput.value && checkOutInput.value) {
            const d1 = new Date(checkInInput.value);
            const d2 = new Date(checkOutInput.value);
            if (!isNaN(d1) && !isNaN(d2)) {
                const diffTime = d2 - d1;
                const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));
                if (diffDays > 0) {
                    nightsInput.value = diffDays;
                    nightsInput.style.backgroundColor = '#e0f2fe';
                    setTimeout(() => { nightsInput.style.backgroundColor = ''; }, 400);
                }
            }
        }

        // 2. Multipliers
        const qtyInput = row.querySelector('input[name$="-quantity"]');
        let qty = 1;
        if (qtyInput && qtyInput.value !== '') {
            qty = parseFloat(qtyInput.value) || 0;
        }

        let nights = 1;
        if (nightsInput && nightsInput.value !== '') {
            nights = parseFloat(nightsInput.value) || 1;
        } else if (timesInput && timesInput.value !== '') {
            nights = parseFloat(timesInput.value) || 1;
        }
        if (nights < 1) nights = 1;

        // 3. Customer Selling Total (Đơn giá báo khách -> Thành tiền báo khách)
        const unitPriceInput = row.querySelector('input[name$="-unit_price"]');
        const sellingTotalInput = row.querySelector('input[name$="-selling_total_price"]') || row.querySelector('input[name$="-custom_total_price"]');

        if (unitPriceInput && sellingTotalInput) {
            let unitPrice = 0;
            if (unitPriceInput.value !== '') {
                unitPrice = parseFloat(unitPriceInput.value.replace(/,/g, '')) || 0;
            }
            if (unitPrice > 0 || (qtyInput && qtyInput.value !== '')) {
                const sellingTotal = Math.round(qty * nights * unitPrice);
                sellingTotalInput.value = sellingTotal;
                sellingTotalInput.style.backgroundColor = '#dcfce7';
                setTimeout(() => { sellingTotalInput.style.backgroundColor = ''; }, 400);
            }
        }

        // 4. Supplier Contract Total (Giá HĐ NCC -> Tổng chi phí NCC)
        const contractUnitInput = row.querySelector('input[name$="-contract_unit_price"]');
        const contractTotalInput = row.querySelector('input[name$="-contract_total_price"]');

        if (contractUnitInput && contractTotalInput) {
            let contractUnitPrice = 0;
            if (contractUnitInput.value !== '') {
                contractUnitPrice = parseFloat(contractUnitInput.value.replace(/,/g, '')) || 0;
            }
            if (contractUnitPrice > 0 || (qtyInput && qtyInput.value !== '')) {
                const contractTotal = Math.round(qty * nights * contractUnitPrice);
                contractTotalInput.value = contractTotal;
                contractTotalInput.style.backgroundColor = '#fef3c7';
                setTimeout(() => { contractTotalInput.style.backgroundColor = ''; }, 400);
            }
        }
    }

    // Event listener for user inputs
    document.addEventListener('input', function(e) {
        const target = e.target;
        if (!target.name) return;

        if (
            target.name.endsWith('-check_in') ||
            target.name.endsWith('-check_out') ||
            target.name.endsWith('-service_date') ||
            target.name.endsWith('-end_date') ||
            target.name.endsWith('-quantity') ||
            target.name.endsWith('-nights') ||
            target.name.endsWith('-times') ||
            target.name.endsWith('-unit_price') ||
            target.name.endsWith('-contract_unit_price')
        ) {
            const row = target.closest('tr') || target.closest('.form-row') || target.closest('.inline-related');
            calculateRow(row);
        }
    });

    document.addEventListener('change', function(e) {
        const target = e.target;
        if (!target.name) return;

        if (
            target.name.endsWith('-check_in') ||
            target.name.endsWith('-check_out') ||
            target.name.endsWith('-service_date') ||
            target.name.endsWith('-end_date') ||
            target.name.endsWith('-quantity') ||
            target.name.endsWith('-nights') ||
            target.name.endsWith('-times') ||
            target.name.endsWith('-unit_price') ||
            target.name.endsWith('-contract_unit_price')
        ) {
            const row = target.closest('tr') || target.closest('.form-row') || target.closest('.inline-related');
            calculateRow(row);
        }
    });

    // Handle dynamically added rows
    document.addEventListener('formset:added', function(event) {
        const newRow = event.target;
        if (newRow) {
            const qtyInput = newRow.querySelector('input[name$="-quantity"]');
            const nightsInput = newRow.querySelector('input[name$="-nights"]');
            const timesInput = newRow.querySelector('input[name$="-times"]');
            if (qtyInput && !qtyInput.value) qtyInput.value = 1;
            if (nightsInput && !nightsInput.value) nightsInput.value = 1;
            if (timesInput && !timesInput.value) timesInput.value = 1;
            calculateRow(newRow);
        }
    });
});
