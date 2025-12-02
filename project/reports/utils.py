# reports/utils.py
import csv
from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def export_assets_csv(queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="assets.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name','Category','Brand','Serial','Purchase Date','Warranty Expiry','Status','Cost'])
    for a in queryset:
        writer.writerow([a.name, a.category.name, a.brand, a.serial_number, a.purchase_date, a.warranty_expiry, a.status, a.cost])
    return response

def export_assets_pdf(queryset):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    y = 750
    p.setFont("Helvetica", 10)
    p.drawString(50, y+20, "Assets Report")
    for a in queryset:
        line = f"{a.name} | {a.serial_number} | {a.category.name} | {a.status}"
        p.drawString(50, y, line)
        y -= 14
        if y < 50:
            p.showPage()
            y = 750
    p.save()
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')
