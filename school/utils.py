import csv
import io
import os
from django.http import HttpResponse
from django.utils.text import slugify
from django.db import models
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import openpyxl


def _get_field_value(obj, field_name):
    val = getattr(obj, field_name)
    field = obj._meta.get_field(field_name)
    if isinstance(field, (models.ImageField, models.FileField)):
        return val.url if val else ''
    if isinstance(field, models.ForeignKey):
        return str(getattr(obj, field_name)) if getattr(obj, field_name) else ''
    try:
        val = val() if callable(val) else val
        return str(val) if not isinstance(val, (str, int, float)) else val
    except Exception:
        return str(val)


def export_csv(queryset, model_name):
    opts = queryset.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={model_name}.csv'
    writer = csv.writer(response)
    fields = [field for field in opts.fields if field.name != 'id']
    writer.writerow([f.verbose_name.title() for f in fields])
    for obj in queryset:
        row = [_get_field_value(obj, f.name) for f in fields]
        writer.writerow(row)
    return response


def export_excel(queryset, model_name):
    opts = queryset.model._meta
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename={model_name}.xlsx'
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = model_name
    fields = [field for field in opts.fields if field.name != 'id']
    ws.append([f.verbose_name.title() for f in fields])
    for obj in queryset:
        row = [_get_field_value(obj, f.name) for f in fields]
        ws.append(row)
    wb.save(response)
    return response


def generate_pdf_report(title, data, headers, filename):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={filename}.pdf'
    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Spacer(1, 20))
    table_data = [headers]
    table_data.extend(data)
    table = Table(table_data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table.setStyle(style)
    elements.append(table)
    doc.build(elements)
    return response


def generate_fee_receipt_pdf(payment, school_name):
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    font_path = os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts', 'arial.ttf')
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('ArialUni', font_path))
        pdfmetrics.registerFont(TTFont('ArialUni-Bold', os.path.join(os.environ.get('WINDIR', r'C:\Windows'), 'Fonts', 'arialbd.ttf')))
        FONT_NAME = 'ArialUni'
        FONT_BOLD = 'ArialUni-Bold'
    else:
        FONT_NAME = 'Helvetica'
        FONT_BOLD = 'Helvetica-Bold'

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, topMargin=15*mm, bottomMargin=15*mm)
    styles = getSampleStyleSheet()
    style_heading = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceAfter=6, alignment=TA_CENTER, fontName=FONT_BOLD)
    style_copy = ParagraphStyle('CopyLabel', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, spaceBefore=4, textColor=colors.gray, fontName=FONT_NAME)
    style_amount = ParagraphStyle('Amount', parent=styles['Normal'], fontSize=14, alignment=TA_RIGHT, spaceAfter=4, fontName=FONT_BOLD)
    style_label = ParagraphStyle('Label', parent=styles['Normal'], fontSize=10, fontName=FONT_BOLD)
    style_value = ParagraphStyle('Value', parent=styles['Normal'], fontSize=10, fontName=FONT_NAME)
    style_normal = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=10, spaceAfter=4, fontName=FONT_NAME)
    style_footer = ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.gray, fontName=FONT_NAME)

    enrollment = payment.student.enrollments.first()
    class_name = str(enrollment.class_enrolled) if enrollment else '-'

    def make_copy_block(label):
        data = [
            [Paragraph(school_name, style_heading)],
            [Paragraph(f'<b>Fee Payment Receipt</b>', ParagraphStyle('SubHead', parent=styles['Normal'], fontSize=11, alignment=TA_CENTER))],
            [Paragraph(f'<i>{label}</i>', style_copy)],
            [HRFlowable(width='100%', thickness=1, color=colors.HexColor('#667eea'))],
        ]

        fields = [
            ('Receipt #:', payment.receipt_number),
            ('Transaction ID:', payment.transaction_id or '-'),
            ('Date:', str(payment.payment_date)),
            ('Payment Method:', payment.get_payment_method_display()),
        ]
        for fname, fval in fields:
            row = [
                [Paragraph(f'<b>{fname}</b>', style_label), Paragraph(f'{fval}', style_value)],
            ]
            t = Table(row, colWidths=[100, 300])
            t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
            data.append([t])

        data.append([HRFlowable(width='100%', thickness=0.5)])
        info_rows = [
            ('Student:', payment.student.full_name),
            ('Class:', class_name),
            ('Fee Type:', payment.fee_structure.get_fee_type_display()),
            ('Description:', payment.fee_structure.description or '-'),
        ]
        for fname, fval in info_rows:
            row = [
                [Paragraph(f'<b>{fname}</b>', style_label), Paragraph(f'{fval}', style_value)],
            ]
            t = Table(row, colWidths=[100, 300])
            t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'MIDDLE'), ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2)]))
            data.append([t])

        data.append([HRFlowable(width='100%', thickness=1, color=colors.HexColor('#667eea'))])
        data.append([Paragraph(f'<b>Amount Paid: \u20b9{payment.amount_paid:.2f}</b>', style_amount)])
        data.append([HRFlowable(width='100%', thickness=1, color=colors.HexColor('#667eea'))])
        data.append([Paragraph('Thank you for the payment!', ParagraphStyle('Thanks', parent=styles['Normal'], fontSize=9, alignment=TA_CENTER, textColor=colors.gray))])
        data.append([Paragraph('This is a computer-generated receipt.', ParagraphStyle('Fine', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.gray))])

        t = Table(data, colWidths=[400])
        t.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ]))
        return t

    elements = []
    elements.append(make_copy_block('OFFICE COPY'))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph('<i>~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~  CUT HERE  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~</i>', ParagraphStyle('CutLine', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.gray)))
    elements.append(Spacer(1, 8))
    elements.append(make_copy_block('CUSTOMER COPY'))

    doc.build(elements)
    buf.seek(0)
    response = HttpResponse(buf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=receipt_{payment.receipt_number}.pdf'
    return response
