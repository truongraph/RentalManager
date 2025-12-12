

/* 1. Lấy danh sách tất cả các phòng (kể cả trạng thái) */
SELECT
    room_id, name_room, area_m2, floor, base_rent,
    electric_unit_price, water_unit_price,
    status, note
FROM room
WHERE is_deleted = 0
ORDER BY floor, name_room;


/* 2. Lấy danh sách phòng đang trống (available) */
SELECT
    room_id, name_room, area_m2, floor, base_rent
FROM room
WHERE status = 'available' AND is_deleted = 0
ORDER BY floor, name_room;


/* 3. Lấy thông tin phòng kèm hợp đồng hiện tại (nếu có) */
SELECT
    r.room_id, r.name_room, r.status,
    c.contract_id, c.start_ymd, c.end_ymd, c.contract_status,
    t.full_name AS tenant_name, t.phone
FROM room r
LEFT JOIN contract c ON r.room_id = c.room_id
    AND c.contract_status = 'active'
    AND c.is_deleted = 0
LEFT JOIN tenant t ON c.tenant_id = t.tenant_id AND t.is_deleted = 0
WHERE r.is_deleted = 0
ORDER BY r.floor, r.name_room;


/* 4. Lấy danh sách hợp đồng đang hiệu lực (active) */
SELECT
    c.contract_id, c.name_contact, c.start_ymd, c.end_ymd,
    r.name_room, t.full_name, t.phone
FROM contract c
JOIN room r ON c.room_id = r.room_id
JOIN tenant t ON c.tenant_id = t.tenant_id
WHERE c.contract_status = 'active' AND c.is_deleted = 0
ORDER BY c.start_ymd DESC;


/* 5. Lấy tất cả hóa đơn của một hợp đồng cụ thể */
/* Thay :contract_id bằng ID hợp đồng thực tế */
SELECT
    bill_id, bill_code, bill_month,
    elec_prev, elec_current, water_prev, water_current,
    room_rent_amount, other_fee, total_amount,
    paid_amount, paid_status, paid_ymd
FROM bill
WHERE contract_id = :contract_id AND is_deleted = 0
ORDER BY bill_month DESC;


/* 6. Lấy hóa đơn chưa thanh toán (toàn bộ) */
SELECT
    b.bill_id, b.bill_code, b.bill_month, b.total_amount,
    r.name_room, t.full_name
FROM bill b
JOIN contract c ON b.contract_id = c.contract_id
JOIN room r ON c.room_id = r.room_id
JOIN tenant t ON c.tenant_id = t.tenant_id
WHERE b.paid_status = 'unpaid' AND b.is_deleted = 0
ORDER BY b.bill_month;


/* 7. Thống kê doanh thu theo tháng (tổng tiền đã thu) */
SELECT
    strftime('%m/%Y', paid_ymd) AS month_year,
    SUM(paid_amount) AS total_paid
FROM bill
WHERE paid_status = 'paid' AND is_deleted = 0
GROUP BY strftime('%m/%Y', paid_ymd)
ORDER BY month_year DESC;


/* 8. Lấy thông tin chi tiết một hóa đơn (dùng để in PDF) */
/* Thay :bill_id bằng ID hóa đơn thực tế */
SELECT
    b.bill_code, b.bill_month,
    r.name_room, r.base_rent,
    t.full_name, t.phone, t.id_number,
    c.name_contact, c.deposit_amount,
    b.elec_prev, b.elec_current,
    (b.elec_current - b.elec_prev) AS elec_used,
    b.water_prev, b.water_current,
    (b.water_current - b.water_prev) AS water_used,
    b.electric_unit_price, b.water_unit_price,
    b.room_rent_amount, b.other_fee, b.total_amount,
    b.paid_amount, b.paid_status, b.paid_ymd
FROM bill b
JOIN contract c ON b.contract_id = c.contract_id
JOIN room r ON c.room_id = r.room_id
JOIN tenant t ON c.tenant_id = t.tenant_id
WHERE b.bill_id = :bill_id AND b.is_deleted = 0;


/* 9. Lấy danh sách khách thuê hiện tại (đang ở) */
SELECT
    t.tenant_id, t.full_name, t.phone, t.id_number,
    r.name_room, c.start_ymd, c.deposit_amount
FROM tenant t
JOIN contract c ON t.tenant_id = c.tenant_id
    AND c.contract_status = 'active' AND c.is_deleted = 0
JOIN room r ON c.room_id = r.room_id
WHERE t.is_deleted = 0;


/* 10. Tìm kiếm phòng hoặc khách theo tên/số điện thoại */
/* Thay :search bằng từ khóa tìm kiếm */
SELECT
    r.name_room, t.full_name, t.phone, c.contract_status
FROM room r
LEFT JOIN contract c ON r.room_id = c.room_id
    AND c.contract_status = 'active' AND c.is_deleted = 0
LEFT JOIN tenant t ON c.tenant_id = t.tenant_id
WHERE (r.name_room LIKE '%' || :search || '%'
    OR t.full_name LIKE '%' || :search || '%'
    OR t.phone LIKE '%' || :search || '%')
  AND r.is_deleted = 0;