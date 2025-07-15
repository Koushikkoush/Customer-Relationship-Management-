from django.urls import path

from . import views

app_name = 'team'

urlpatterns = [
    path('', views.teams_list, name='list'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/edit/', views.edit_team, name='edit'),
    path('<int:pk>/activate/', views.teams_activate, name='activate'),
    path('manage-roles/', views.manage_roles, name='manage_roles'),
    path('change-role/<int:user_id>/', views.change_role, name='change_role'),
]