from openpyxl import Workbook
from django.http import HttpResponse
import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

def export_accepted_applicants_to_excel(applications, company_name):
    wb = Workbook()
    ws = wb.active
    ws.title = "Accepted Applicants"
    headers = [
        "Applicant Username",
        "Applicant Email",
        "Job Title",
        "Company",
        "Status",
    ]
    ws.append(headers)
    for application in applications:
        profile = application.applicant.userprofile
        resume_url = application.get_resume() or "No resume"
        ws.append([
            application.applicant.username,
            application.applicant.email,
            application.job.title,
            application.job.company,
            application.status,
        ])
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    safe_company_name = company_name.replace(" ", "_").replace("/", "_")
    filename = f"{safe_company_name}_accepted_applicants_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response["Content-Disposition"] = f"attachment; filename={filename}"
    wb.save(response)
    return response

def export_accepted_applicants_to_pdf(applications, company_name):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Accepted Applicants for {company_name}", styles['Title']))
    data = [[
        "Username",
        "Email",
        "Job Title",
        "Company",
        "Status",
    ]]
    for application in applications:
        profile = application.applicant.userprofile
        resume_url = application.get_resume() or "No resume"
        data.append([
            application.applicant.username,
            application.applicant.email,
            application.job.title,
            application.job.company,
            application.status,
        ])
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    safe_company_name = company_name.replace(" ", "_").replace("/", "_")
    filename = f"{safe_company_name}_accepted_applicants_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f"attachment; filename={filename}"
    response.write(pdf)
    return response