from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    path("", views.home, name='home'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path("test/", views.test, name='test'),
    path("signup/", views.signup, name="signup"),
    path("verify-account/", views.verify_email, name="verify_email"),
    path('change-password/', views.passChangeView, name='password_change'),
    path('forgot-password/', views.password_reset_request, name='password_reset'),
    path('password-reset-done/', views.password_email, name='password_email'),
    path('faculty/create-parent', views.create_parent_account, name='parent_account'),

    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('logout/', views.logoutView, name='logout'),
    # path('login1/', views.loginView, name='login'),
    path("faculty/create-job", views.post_job, name="post_job"),
    path('faculty/jobs/', views.facultyJobList, name="faculty_job_list"),
    path('faculty/job/<int:job_id>/applications', views.jobApplicationDBFaculty, name='job_applications'),
    path('student/apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('detail/<int:job_id>/', views.jobDetail, name='job_detail'),
    path('student/job-status/', views.jobApplicationStatus, name='job_status'),
    path('faculty/edit-status/<int:application_id>/', views.updateApplicationStatus, name='edit_status'),
    path('faculty/manage-jobs/', views.deleteJobList, name='manage_jobs'),
    path('faculty/delete-job/<int:job_id>/', views.deleteJobPost, name='delete_job'),
    path('job-list', views.jobList, name='job_list'),
    path('jobsearch/', views.job_search, name='job-search'),
    path('jobs/edit/<int:job_id>/', views.editJob, name='edit_job')

]