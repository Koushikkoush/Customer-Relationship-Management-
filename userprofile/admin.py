from django.contrib import admin
from .models import Userprofile, Role

class UserprofileAdmin(admin.ModelAdmin):
    list_display = ['user', 'active_team', 'role']
    list_filter = ['active_team', 'role']
    search_fields = ['user__username', 'user__email']

admin.site.register(Userprofile, UserprofileAdmin)
admin.site.register(Role)