from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from xhtml2pdf import pisa
from io import BytesIO
from django.utils.timezone import now


from django.utils.timezone import now
from django.conf import settings

from SmartLearn import settings

def generate_certificate_pdf(user, course):
    html = render_to_string(
        "certificates/certificate_v2.html",
        {
            "student_name": user.get_full_name() or user.username,
            "course_title": course.title,
            "issue_date": now().strftime("%B %d, %Y"),
            "STATIC_URL": settings.STATIC_URL
        }
        )


    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)

    if pisa_status.err:
        return None

    file_name = f"certificate_{user.id}_{course.id}.pdf"
    return ContentFile(result.getvalue(), name=file_name)
