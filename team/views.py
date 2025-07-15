from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from .forms import TeamForm
from .models import Team
from userprofile.models import Userprofile, Role
from core.decorators import role_required


@login_required
def teams_list(request):
    teams = Team.objects.filter(members__in=[request.user])

    return render(request, 'team/teams_list.html', {'teams': teams})


@login_required
def teams_activate(request, pk):
    team = Team.objects.filter(members__in=[request.user]).get(pk=pk)
    userprofile = request.user.userprofile
    userprofile.active_team = team
    userprofile.save()

    return redirect('team:detail', pk=pk)


@login_required
def detail(request, pk):
    team = get_object_or_404(Team, members__in=[request.user], pk=pk)

    return render(request, 'team/detail.html', {'team': team})


@login_required
def edit_team(request, pk):
    team = get_object_or_404(Team, created_by=request.user, pk=pk)

    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)

        if form.is_valid():
            form.save()

            messages.success(request, 'The changes was saved!')

            return redirect('userprofile:myaccount')
    else:
        form = TeamForm(instance=team)

    return render(request, 'team/edit_team.html', {
        'team': team,
        'form': form
    })


@login_required
@role_required(['admin'])
def manage_roles(request):
    team = request.user.userprofile.active_team
    team_members = Userprofile.objects.filter(active_team=team)
    
    return render(request, 'team/manage_roles.html', {
        'team': team,
        'team_members': team_members
    })

@login_required
@role_required(['admin'])
def change_role(request, user_id):
    team = request.user.userprofile.active_team
    user_profile = get_object_or_404(Userprofile, user_id=user_id, active_team=team)
    available_roles = Role.objects.filter(team=team)
    
    if request.method == 'POST':
        role_id = request.POST.get('role')
        if role_id:
            role = get_object_or_404(Role, id=role_id, team=team)
            user_profile.role = role
            user_profile.save()
            messages.success(request, f"Role updated for {user_profile.user.username}")
        return redirect('team:manage_roles')
    
    return render(request, 'team/change_role.html', {
        'user_profile': user_profile,
        'available_roles': available_roles
    })