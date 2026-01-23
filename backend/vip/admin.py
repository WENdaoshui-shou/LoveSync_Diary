from django.contrib import admin
from .models import VIPMember, VIPPrivilege, VIPOrder

# Register your models here.
admin.site.register(VIPMember)
admin.site.register(VIPPrivilege)
admin.site.register(VIPOrder)
