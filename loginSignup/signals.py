from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from .models import CreateJob
from loginSignup.models import CustomUser  # adjust if needed

@receiver(post_save, sender=CreateJob)
def send_job_email(sender, instance, created, **kwargs):
    if created:
        job_url = f"http://{settings.DOMAIN}/detail/{instance.id}/"

        subject = f"New Job Posted: {instance.title}"
        from_email = settings.DEFAULT_FROM_EMAIL

        users = CustomUser.objects.all()
        recipient_list = [user.email for user in users if user.email]

        for email in recipient_list:
            text_content = (
                f"New job alert!\n\n"
                f"Title: {instance.title}\n"
                f"Company: {instance.companyName}\n"
                f"Position: {instance.position}\n\n"
                f"{instance.description}\n\n"
                f"View Job: {job_url}"
            )

            html_content = render_to_string("emails/newJobPost.html", {
                "job": instance,
                "job_url": job_url
            })

            msg = EmailMultiAlternatives(subject, text_content, from_email, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
