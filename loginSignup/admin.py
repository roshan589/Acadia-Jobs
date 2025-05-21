from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(CreateJob)
admin.site.register(ApplyJob)
# Add additional models as needed
