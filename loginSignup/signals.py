from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from .models import CreateJob, ApplyJob
from loginSignup.models import CustomUser  # adjust if needed

@receiver(post_save, sender=CreateJob)
def send_job_email(sender, instance, created, **kwargs):
    if created:
        job_url = f"http://{settings.DOMAIN}/detail/{instance.id}/"

        subject = f"New Job Posted: {instance.title}"
        from_email = settings.DEFAULT_FROM_EMAIL

        users = CustomUser.objects.exclude(id=instance.posted_by.id)
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

@receiver(post_save, sender=ApplyJob)
def send_apply_email(sender, instance, created, **kwargs):
    if created:
        job = instance.job
        faculty = job.posted_by
        application_url = f"http://{settings.DOMAIN}/faculty/job/{job.id}/applications"

        subject = f"New Application for {job.title}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = faculty.email

        if to_email:
            text_content = (
                f"Hello {faculty.first_name},\n\n"
                f"{instance.first_name} {instance.last_name} has applied for your job posting '{job.title}'.\n"
                f"Check the dashboard to view the application."
            )

            html_content = render_to_string("emails/newApplicationReceived.html", {
                "faculty": faculty,
                "job": job,
                "applicant": instance,
                "application_url": application_url
            })

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

@receiver(post_save, sender=ApplyJob)
def notify_applicant_status_change(sender, instance, created, **kwargs):
    if created:
        return
    status_url = f"http://{settings.DOMAIN}/student/job-status/"

    try:
        previous = ApplyJob.objects.get(pk=instance.pk)
    except ApplyJob.DoesNotExist:
        return

    if previous.job_status != instance.job_status:
        applicant = instance.user
        job = instance.job
        new_status = instance.job_status
        status_display = instance.get_job_status_display()

        subject = f"Update on Your Application for '{job.title}'"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = applicant.email
        
        # Customize message based on status
        if new_status == ApplyJob.PENDING:
            message = "Your application has been received and is pending review."
        elif new_status == ApplyJob.IN_REVIEW:
            message = "Your application is currently under review."
        elif new_status == ApplyJob.INTERVIEW:
            message = "Congratulations! You have been selected for an interview."
        elif new_status == ApplyJob.ACCEPTED:
            message = "Good news! Your application has been accepted."
        elif new_status == ApplyJob.REJECTED:
            message = "We regret to inform you that your application was not successful."
        else:
            message = "Your application status has been updated."

        text_content = (
            f"Hello {applicant.first_name},\n\n"
            f"{message}\n\n"
            f"Job: {job.title}\n"
            f"Status: {status_display}\n\n"
            f"Thank you for your interest."
        )

        html_content = render_to_string("emails/jobStatusUpdated.html", {
            "applicant": applicant,
            "job": job,
            "status": status_display,
            "message": message,
            "status_url":status_url
        })

        msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()