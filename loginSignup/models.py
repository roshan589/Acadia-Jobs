import string

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail
from django.db import models
import random
from django.conf import settings



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)  # Track if user has verified their email
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=(('student', 'Student'), ('faculty', 'Faculty')))

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'user_type']

    def __str__(self):
        return self.email

    def generateVerificationCode(self):
        """Generate a random 6-digit verification code."""
        self.verification_code = ''.join(random.choices(string.digits, k=6))
        self.save()  # Save the code to the database

    def sendVerificationEmail(self):
        """Send the verification code to the user's email."""
        if self.verification_code:
            send_mail(
                'Email Verification',
                f"Hi {self.first_name},\n\nPlease use the following verification code to verify your account:\n\n{self.verification_code}\n\nThank you!",
                'roshanadhikari0420@gmail.com',
                [self.email]
            )


class CreateJob(models.Model):
    title = models.CharField(max_length=200)
    position = models.CharField(max_length=100)
    companyName = models.CharField(max_length=100)
    description = models.TextField()
    posted_by = models.ForeignKey('loginSignup.CustomUser', on_delete=models.CASCADE)
    posted_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ApplyJob(models.Model):
    PENDING = 'pending'
    IN_REVIEW = 'under_review'
    INTERVIEW = 'inteview'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

    JOB_STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (IN_REVIEW, 'Under Review'),
        (INTERVIEW, 'Selected for interview'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    )
    job = models.ForeignKey(CreateJob, on_delete=models.CASCADE, related_name='applications')
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=12)
    user = models.ForeignKey('loginSignup.CustomUser', on_delete=models.CASCADE)
    resume = models.FileField(upload_to="resumes/")
    availability_start_date = models.DateField()
    availability_end_date = models.DateField()
    applied_on = models.DateTimeField(auto_now_add=True)
    job_status = models.CharField(max_length=100, choices=JOB_STATUS_CHOICES, default=PENDING)


