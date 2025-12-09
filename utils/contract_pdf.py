# utils/contract_pdf.py
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime
from config import PDF_OUTPUT_DIR, FONT_PATH


# =====================================#
# =====================================#
# =====================================#
def register_fonts():
    regular = FONT_PATH
    bold = FONT_PATH.replace(".ttf", "-Bold.ttf")
    if os.path.exists(regular):
        pdfmetrics.registerFont(TTFont("Inter", regular))
    if os.path.exists(bold):
        pdfmetrics.registerFont(TTFont("Inter-Bold", bold))

# =====================================#
# =====================================#
# =====================================#
register_fonts()


# =====================================#
# =====================================#
# =====================================#
def generate_contract_pdf(
    contract_data, room_data, tenant_data, output_dir=PDF_OUTPUT_DIR
):
    os.makedirs(output_dir, exist_ok=True)
    filename = f"HopDong_{contract_data['contract_id']:04d}_{tenant_data['full_name'].replace(' ', '_')}.pdf"
    filepath = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        topMargin=1.8 * cm,
        bottomMargin=2.0 * cm,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
    )

    story = []

    styles = {
        "center": ParagraphStyle(
            name="Center",
            fontName="Inter-Bold",
            fontSize=12.5,
            alignment=TA_CENTER,
            spaceAfter=8,
            textColor=colors.HexColor("#0f172a"),
        ),
        "title": ParagraphStyle(
            name="Title",
            fontName="Inter-Bold",
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=16,
            textColor=colors.HexColor("#0f172a"),
        ),
        "subtitle": ParagraphStyle(
            name="Subtitle",
            fontName="Inter-Bold",
            fontSize=13,
            alignment=TA_LEFT,
            spaceAfter=8,
            textColor=colors.HexColor("#0f172a"),
        ),
        "normal": ParagraphStyle(
            name="Normal",
            fontName="Inter",
            fontSize=11.5,
            leading=18,
            alignment=TA_LEFT,
            spaceAfter=5,
        ),
        "bold_text": ParagraphStyle(
            name="BoldText", fontName="Inter-Bold", fontSize=11.5, leading=18
        ),
        "meta_center": ParagraphStyle(
            name="MetaCenter",
            fontName="Inter",
            fontSize=11.5,
            alignment=TA_CENTER,
            spaceAfter=5,
            textColor=colors.HexColor("#334155"),
        ),
    }

    story.append(Paragraph("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", styles["center"]))
    story.append(Paragraph("Độc lập - Tự do - Hạnh phúc", styles["center"]))
    story.append(Spacer(1, 16))
    story.append(Paragraph("HỢP ĐỒNG THUÊ PHÒNG TRỌ", styles["title"]))
    story.append(
        Paragraph(
            f"Số hợp đồng: <b>{contract_data['contract_id']}</b>", styles["meta_center"]
        )
    )
    story.append(
        Paragraph(
            f"Ngày lập hợp đồng: <b>{datetime.now().strftime('%d/%m/%Y')}</b>",
            styles["meta_center"],
        )
    )
    story.append(Spacer(1, 10))
    story.append(Paragraph("BÊN A (BÊN CHO THUÊ)", styles["subtitle"]))
    story.append(
        Paragraph("• Công ty/Tổ chức: <b>CÔNG TY QUẢN LÝ NHÀ TRỌ</b>", styles["normal"])
    )
    story.append(Paragraph("• Đại diện: <b>Ông NGUYỄN VĂN A</b>", styles["normal"]))
    story.append(Paragraph("• Chức vụ: Chủ nhà trọ", styles["normal"]))
    story.append(
        Paragraph(
            "• Địa chỉ: 23 Đường ABC, Phường 5, Quận 1, TP. Hồ Chí Minh",
            styles["normal"],
        )
    )
    story.append(Paragraph("• Số điện thoại: <b>0123 456 789</b>", styles["normal"]))
    story.append(Paragraph("• CMND/CCCD: <b>0768484671</b>", styles["normal"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("BÊN B (BÊN THUÊ)", styles["subtitle"]))
    story.append(
        Paragraph(f"• Họ và tên: <b>{tenant_data['full_name']}</b>", styles["normal"])
    )
    story.append(
        Paragraph(
            f"• CMND/CCCD: <b>{tenant_data['id_number'] or 'Chưa cung cấp'}</b>",
            styles["normal"],
        )
    )
    story.append(
        Paragraph(
            f"• Số điện thoại: <b>{tenant_data['phone'] or 'Chưa cung cấp'}</b>",
            styles["normal"],
        )
    )
    story.append(
        Paragraph(
            f"• Ngày sinh: <b>{_format_date(tenant_data['birth'])}</b>",
            styles["normal"],
        )
    )
    story.append(
        Paragraph(
            f"• Địa chỉ thường trú: <b>{tenant_data['address'] or 'Chưa cung cấp'}</b>",
            styles["normal"],
        )
    )
    story.append(Spacer(1, 8))
    story.append(Paragraph("THÔNG TIN PHÒNG THUÊ & ĐIỀU KIỆN", styles["subtitle"]))
    story.append(
        Paragraph(f"• Phòng số: <b>{room_data['name_room']}</b>", styles["normal"])
    )
    story.append(
        Paragraph(f"• Diện tích: <b>{room_data['area_m2']} m²</b>", styles["normal"])
    )
    story.append(
        Paragraph(
            f"• Giá thuê/tháng: <b>{_format_currency(contract_data['rent'])} VNĐ</b> (chưa bao gồm điện nước)",
            styles["normal"],
        )
    )
    story.append(
        Paragraph(
            f"• Tiền đặt cọc: <b>{_format_currency(contract_data['deposit_amount'])} VNĐ</b>",
            styles["normal"],
        )
    )
    story.append(
        Paragraph(
            f"• Ngày nhận phòng: <b>{_format_date(contract_data['start_ymd'])}</b>",
            styles["normal"],
        )
    )
    story.append(
        Paragraph(
            f"• Ngày kết thúc: <b>{_format_date(contract_data['end_ymd']) or 'Không xác định'}</b>",
            styles["normal"],
        )
    )
    story.append(
        Paragraph(
            f"• Đồng hồ điện ban đầu: <b>{contract_data['electric_meter_start']}</b>",
            styles["normal"],
        )
    )
    story.append(
        Paragraph(
            f"• Đồng hồ nước ban đầu: <b>{contract_data['water_meter_start']}</b>",
            styles["normal"],
        )
    )
    story.append(
        Paragraph(
            f"• Ngày đặt cọc: <b>{_format_date(contract_data['deposit_ymd'])}</b>",
            styles["normal"],
        )
    )
    story.append(
        Paragraph(f"• Ghi chú: {contract_data['note'] or 'Không có'}", styles["normal"])
    )
    story.append(Spacer(1, 12))
    story.append(PageBreak())
    story.append(Paragraph("ĐIỀU 1: QUYỀN VÀ NGHĨA VỤ BÊN A", styles["subtitle"]))
    story.append(
        Paragraph(
            "• Giao phòng đúng hạn, đảm bảo sạch sẽ, đầy đủ tiện nghi.",
            styles["normal"],
        )
    )
    story.append(
        Paragraph("• Thu tiền thuê và cung cấp hóa đơn nếu yêu cầu.", styles["normal"])
    )
    story.append(
        Paragraph("• Sửa chữa lớn khi hư hỏng không do bên B.", styles["normal"])
    )
    story.append(Spacer(1, 6))
    story.append(Paragraph("ĐIỀU 2: QUYỀN VÀ NGHĨA VỤ BÊN B", styles["subtitle"]))
    story.append(
        Paragraph(
            "• Thanh toán tiền thuê, điện nước đúng hạn (trước ngày 05 hàng tháng).",
            styles["normal"],
        )
    )
    story.append(
        Paragraph(
            "• Giữ gìn tài sản, không cải tạo phòng nếu chưa được phép.",
            styles["normal"],
        )
    )
    story.append(
        Paragraph(
            "• Tuân thủ nội quy: không ồn ào, không nuôi thú, không hút thuốc.",
            styles["normal"],
        )
    )
    story.append(Spacer(1, 6))
    story.append(Paragraph("ĐIỀU 3: CHẤM DỨT HỢP ĐỒNG", styles["subtitle"]))
    story.append(
        Paragraph("• Thông báo trước 30 ngày nếu muốn kết thúc.", styles["normal"])
    )
    story.append(
        Paragraph(
            "• Bên B kết thúc sớm: mất cọc. Bên A kết thúc sớm: hoàn cọc gấp đôi.",
            styles["normal"],
        )
    )
    story.append(Spacer(1, 6))
    story.append(Paragraph("ĐIỀU 4: ĐIỀU KHOẢN CHUNG", styles["subtitle"]))
    story.append(Paragraph("• Hợp đồng có hiệu lực từ ngày ký.", styles["normal"]))
    story.append(
        Paragraph("• Lập thành 02 bản có giá trị pháp lý ngang nhau.", styles["normal"])
    )
    story.append(Spacer(1, 36))

    sig_data = [
        ["ĐẠI DIỆN BÊN A", "ĐẠI DIỆN BÊN B"],
        ["(Ký và ghi rõ họ tên)", "(Ký và ghi rõ họ tên)"],
        ["", ""],
        ["", ""],
        ["", ""],
        ["NGUYỄN VĂN A", f"{tenant_data['full_name']}"],
    ]

    sig_table = Table(sig_data, colWidths=[9 * cm, 9 * cm])

    sig_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONTNAME", (0, 0), (-1, -1), "Inter"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("FONTSIZE", (0, 1), (-1, 1), 10.5),
                ("FONTSIZE", (0, 4), (-1, 4), 12),
                ("LEADING", (0, 4), (-1, 4), 18),
                # khoảng cách tổng thể
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )

    story.append(sig_table)

    doc.build(story)

    return filepath


# =====================================#
# =====================================#
# =====================================#
def _format_currency(amount):
    if amount is None:
        return "0"
    return "{:,}".format(int(amount)).replace(",", ".")


# =====================================#
# =====================================#
# =====================================#
def _format_date(date_str):
    if not date_str or len(date_str) < 10:
        return "Chưa xác định"
    return f"{date_str[8:10]}/{date_str[5:7]}/{date_str[0:4]}"
