# Import necessary Django modules and decorators
from urllib.parse import urlencode
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SignupForm, JobPost, JobApplyForm, StatusUpdateForm, VerificationCode, JobFilterForm, ProfileUpdateForm
from .models import CreateJob, ApplyJob, CustomUser
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from functools import wraps
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.hashers import make_password


# Decorator to ensure only users with user_type 'faculty' can access the view
def faculty_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'user_type') and request.user.user_type == "faculty":
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You do not have permission to access this page.")
    return wrapper


# Decorator to ensure only users with user_type 'student' can access the view
def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if hasattr(request.user, 'user_type') and request.user.user_type == "student":
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You do not have permission to access this page.")
    return wrapper


# User Signup View
def verify_email(request):
    if request.method == 'POST':
        form = VerificationCode(request.POST)
        if form.is_valid():
            input_code = form.cleaned_data['verification_code']
            expected_code = request.session.get('verification_code')
            signup_data = request.session.get('signup_data')

            if input_code == expected_code and signup_data:
                # Create the user
                user = CustomUser(
                    username=signup_data['username'],
                    email=signup_data['email'],
                    password=make_password(signup_data['password']),  # Hash password
                    is_active=True,
                    is_verified=True,
                )
                user.save()

                # Clean up session
                del request.session['signup_data']
                del request.session['verification_code']

                messages.success(request, "Your account has been verified. You can now log in.")
                return redirect('login')
            else:
                messages.error(request, "Invalid verification code.")
    else:
        form = VerificationCode()
    return render(request, 'registration/verifyEmail.html', {'form': form})

@login_required
def passChangeView(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        elif len(new_password) < 8:
            messages.error(request, 'New password must be at least 8 characters long.')
        else:
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Prevents logout
            messages.success(request, 'Your password was successfully changed.')
            return redirect('test')  # or any page you want

    return render(request, 'registration/passChange.html')

# views.py

def verify_email(request):
    if request.method == 'POST':
        form = VerificationCode(request.POST)

        if form.is_valid():
            code = form.cleaned_data['verification_code']
            try:
                # Try to find the user with the entered verification code
                user = CustomUser.objects.get(verification_code=code)

                # If code matches, verify the user
                if user.verification_code == code:
                    user.is_verified = True
                    user.is_active = True  # Now the user can log in
                    user.save()

                    messages.success(request, "Your account has been verified. You can now log in.")
                    return redirect('login')  # Redirect to login page
                else:
                    messages.error(request, "Invalid verification code.")
            except CustomUser.DoesNotExist:
                messages.error(request, "Verification code does not exist.")

    else:
        form = VerificationCode()  # Instantiate the form for GET request

    return render(request, 'registration/verifyEmail.html', {'form': form})


# Logout View
def logoutView(request):
    logout(request)
    return redirect('home')  # Redirect to home page after logout


# Home page view
def home(request):
    return render(request, "home.html")


# Test page view, shows dashboard based on user role
@login_required(login_url='/login')
def test(request): 
    job_posts = CreateJob.objects.all()
    form = JobFilterForm(request.POST)
    if request.method == "POST":
        form = JobFilterForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            posted_on = form.cleaned_data.get('posted_on')

            if title:
                job_posts = job_posts.filter(title__icontains=title)
            if posted_on:
                job_posts = job_posts.filter(posted_date=posted_on)
            return redirect('job-search')
        
    user_type = getattr(request.user, 'user_type', 'guest')
    context = {
        'role': user_type.capitalize(),
        'can_see_applications': user_type == 'faculty',
        'can_post_jobs': user_type == 'faculty',
        'can_see_jobApplicationStatus': user_type == 'student',
        'form': form,
        'can_manage_jobs': user_type == 'faculty',
    }
    return render(request, "test.html", context)



@login_required(login_url='/login')
def job_search(request):
    job_posts = CreateJob.objects.none()  # Don't load all initially
    form = JobFilterForm(request.GET)

    if form.is_valid():
        title = form.cleaned_data.get('title')
        posted_on = form.cleaned_data.get('posted_on')

        job_posts = CreateJob.objects.all()
        if title:
            job_posts = job_posts.filter(title__icontains=title)
        if posted_on:
            job_posts = job_posts.filter(posted_date=posted_on)

    return render(request, 'jobSearch.html', {
        'form': form,
        'job_posts': job_posts
    })




# View to list all jobs (available to all logged-in users)
@login_required(login_url="/login")
def jobList(request):
    job_posts = CreateJob.objects.all()
    context = {
        'job_posts': job_posts,
    }
    return render(request, "joblist.html", context)


@login_required(login_url="/login")
def jobDetail(request, job_id):
    job = get_object_or_404(CreateJob, id=job_id)
    return render(request, 'jobDetail.html', {'job': job})

# Student-only view to apply for a job
@login_required(login_url="/login")
@student_required
def apply_job(request, job_id):
    job = get_object_or_404(CreateJob, id=job_id)

    if ApplyJob.objects.filter(job=job, user=request.user).exists():
        messages.error(request, 'You have already applied for this job.')
        return redirect('job_list')

    if request.method == "POST":
        form = JobApplyForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.user = request.user
            application.save()
            messages.success(request, "Job Application Submitted.")
            return redirect('job_list')
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email
        }
        form = JobApplyForm(initial=initial_data)

    return render(request, "jobapplication.html", {'form': form, 'job': job})


@login_required(login_url="/login")
@student_required
def jobApplicationStatus(request):
    # Get the current logged-in student
    student = request.user

    # Fetch job applications for the student
    applications = ApplyJob.objects.filter(user=student)

    return render(request, 'jobApplicationStatus.html', {
        'applications': applications
    })


# Faculty-only view to create/post a new job
@login_required(login_url="/login")
@faculty_required
def post_job(request):
    if request.method == "POST":
        form = JobPost(request.POST)
        if form.is_valid():
            job = form.save(commit=False)  # Delay saving to assign 'posted_by'
            job.posted_by = request.user
            job.save()
            messages.success(request, "Job Posted Successfully!")
            return redirect('test')  # Redirect to dashboard after posting

    else:
        form = JobPost()
    return render(request, "createJob.html", {'form': form})


@login_required(login_url="/login")
@faculty_required
def editJob(request, job_id):
    job = get_object_or_404(CreateJob, id=job_id, posted_by=request.user)
    if request.method == "POST":
        form = JobPost(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job Updated Successfully!")
            return redirect('test')
    else:
        form = JobPost(instance=job)

    return render(request, "createJob.html", {'form': form, 'edit': True})




# Faculty-only view to see applications submitted for their posted jobs
@login_required(login_url="/login")
@faculty_required
def jobApplicationDBFaculty(request, job_id):
    print(request.user.user_type)  # Debug print (can be removed in production)
    my_jobs = CreateJob.objects.filter(posted_by=request.user)
    applications = ApplyJob.objects.filter(job__posted_by=request.user).select_related('job', 'user').all()
    return render(request, "jobApplicationList.html", {'applications': applications})


# Faculty-only view to see list of jobs posted by themselves
@login_required(login_url="/login")
@faculty_required
def facultyJobList(request):
    jobs = CreateJob.objects.filter(posted_by=request.user)
    return render(request, "facultyJobList.html", {'jobs': jobs})


@login_required(login_url="/login")
@faculty_required
def updateApplicationStatus(request, application_id):
    application = get_object_or_404(ApplyJob, id=application_id)
    if request.method == "POST":
        form = StatusUpdateForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            return redirect("faculty_job_list")
    else:
        form = StatusUpdateForm(instance=application)
    return render(request, 'updateStatus.html', {'form': form, 'application': application})


@login_required(login_url="/login")
@faculty_required
def deleteJobList(request):
    jobs = CreateJob.objects.filter(posted_by=request.user)
    return render(request, 'deleteJobList.html', {'jobs': jobs})


@login_required(login_url="/login")
@faculty_required
def deleteJobPost(request, job_id):
    job = get_object_or_404(CreateJob, id=job_id)
    if request.method == "POST":
        job.delete()
        return redirect('manage_jobs')
    return render(request, 'deleteJobDetail.html',{'job': job})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile Updated Successfully!")
            return redirect('test')  # Or any other page you prefer
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'updateProfile.html', {'form': form})
