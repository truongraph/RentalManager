# utils/bill_pdf.py
from reportlab.lib.pagesizes import A5
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime
from config import PDF_OUTPUT_DIR, FONT_PATH


# ================== ĐĂNG KÝ FONT INTER ==================
def register_fonts():
    regular = FONT_PATH
    bold = FONT_PATH.replace(".ttf", "-Bold.ttf")
    if os.path.exists(regular):
        pdfmetrics.registerFont(TTFont("Inter", regular))
    if os.path.exists(bold):
        pdfmetrics.registerFont(TTFont("Inter-Bold", bold))

register_fonts()


def generate_bill_pdf(bill_data, output_dir=PDF_OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)

    filename = f"HoaDon_{bill_data['bill_code']}_{bill_data['bill_month'].replace('/', '')}.pdf"
    filepath = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A5,
        topMargin=1.3*cm,
        bottomMargin=1.5*cm,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm
    )

    story = []

    # ================== STYLE – NHỎ GỌN, ĐẸP ==================
    styles = {
        "title": ParagraphStyle(
            name="Title",
            fontName="Inter-Bold",
            fontSize=13,
            alignment=TA_CENTER,
            spaceAfter=10,
            textColor=colors.HexColor("#0f172a")
        ),
        "info_right": ParagraphStyle(   # Mã HĐ, Kỳ, Ngày → căn phải
            name="InfoRight",
            fontName="Inter",
            fontSize=9,
            alignment=TA_LEFT,
            spaceAfter=4
        ),
        "subtitle": ParagraphStyle(
            name="Subtitle",
            fontName="Inter-Bold",
            fontSize=10,
            alignment=TA_LEFT,
            spaceAfter=6
        ),
        "normal": ParagraphStyle(
            name="Normal",
            fontName="Inter",
            fontSize=9.5,
            leading=13,
            alignment=TA_LEFT,
            spaceAfter=3
        ),
        "total_label": ParagraphStyle(
            name="TotalLabel",
            fontName="Inter-Bold",
            fontSize=11,
            alignment=TA_LEFT,
            spaceAfter=4
        ),
        "total_amount": ParagraphStyle(
            name="TotalAmount",
            fontName="Inter-Bold",
            fontSize=13,
            alignment=TA_RIGHT,
            textColor=colors.HexColor("#dc2626")
        ),
        "status": ParagraphStyle(
            name="Status",
            fontName="Inter",
            fontSize=9.5,
            alignment=TA_LEFT,
            spaceAfter=3
        )
    }

    # ================== HEADER – MÃ HĐ, KỲ, NGÀY Ở TRÊN PHẢI ==================
    story.append(Paragraph("PHIẾU THU TIỀN PHÒNG", styles["title"]))

    header_right = [
        Paragraph(f"Mã HĐ: {bill_data['bill_code']}", styles["info_right"]),
        Paragraph(f"Kỳ thanh toán: {bill_data['bill_month']}", styles["info_right"]),
        Paragraph(f"Ngày lập: {datetime.now().strftime('%d/%m/%Y')}", styles["info_right"]),
    ]
    for p in header_right:
        story.append(p)
    story.append(Spacer(1, 10))

    # ================== THÔNG TIN KHÁCH ==================
    story.append(Paragraph("THÔNG TIN KHÁCH THUÊ", styles["subtitle"]))
    story.append(Paragraph(f"• Họ tên: {bill_data['full_name']}", styles["normal"]))
    story.append(Paragraph(f"• Phòng: {bill_data['name_room']}", styles["normal"]))
    story.append(Spacer(1, 8))

    # ================== CHI TIẾT THANH TOÁN ==================
    story.append(Paragraph("CHI TIẾT THANH TOÁN", styles["subtitle"]))

    story.append(Paragraph(f"Tiền thuê phòng: {format_currency(bill_data['room_rent_amount'])} VNĐ", styles["normal"]))

    elec_used = bill_data['elec_current'] - bill_data['elec_prev']
    water_used = bill_data['water_current'] - bill_data['water_prev']

    story.append(Paragraph(f"Điện: {bill_data['elec_prev']} → {bill_data['elec_current']} kWh "
                           f"(dùng {elec_used} kWh × {_format_price(bill_data['electric_unit_price'])})", styles["normal"]))
    story.append(Paragraph(f"     = {format_currency(elec_used * bill_data['electric_unit_price'])} VNĐ", styles["normal"]))

    story.append(Paragraph(f"Nước: {bill_data['water_prev']} → {bill_data['water_current']} m³ "
                           f"(dùng {water_used} m³ × {_format_price(bill_data['water_unit_price'])})", styles["normal"]))
    story.append(Paragraph(f"     = {format_currency(water_used * bill_data['water_unit_price'])} VNĐ", styles["normal"]))

    if bill_data.get('other_fee', 0) > 0:
        story.append(Paragraph(f"Phí khác: {format_currency(bill_data['other_fee'])} VNĐ", styles["normal"]))

    if bill_data.get('note'):
        story.append(Paragraph(f"Ghi chú: {bill_data['note']}", styles["normal"]))

    story.append(Spacer(1, 12))

    # ================== TỔNG CỘNG – KHÔNG TABLE, 2 DÒNG ĐẸP ==================
    story.append(Paragraph(f"TỔNG CỘNG THANH TOÁN: {format_currency(bill_data['total_amount'])} VNĐ", styles["total_label"]))
    story.append(Spacer(1, 10))

    # ================== TRẠNG THÁI – BÌNH THƯỜNG NHƯ TIỀN PHÒNG ==================
    status_text = "Đã thanh toán" if bill_data['paid_status'] == 'paid' else "Chưa thanh toán"
    story.append(Paragraph(f"Trạng thái: {status_text}", styles["status"]))
    story.append(Spacer(1, 15))

    # ================== XUẤT PDF ==================
    doc.build(story)
    return filepath


# ================== HELPER ==================
def format_currency(amount):
    if amount is None or amount == 0:
        return "0"
    return "{:,}".format(int(amount)).replace(",", ".")


def _format_price(price):
    return "{:,}".format(int(price)).replace(",", ".")