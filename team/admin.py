from django.contrib import admin
from .models import Team
from userprofile.models import Role

class RoleInline(admin.TabularInline):
    model = Role
    extra = 0

class TeamAdmin(admin.ModelAdmin):
    inlines = [RoleInline]
    list_display = ['name', 'created_by']
    search_fields = ['name']

admin.site.register(Team, TeamAdmin)