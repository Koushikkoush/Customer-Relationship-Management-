from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Q
from django.utils import timezone
from lead.models import Lead, Activity
from client.models import Client

@login_required
def dashboard(request):
    team = request.user.userprofile.active_team
    
    # Get only active leads and clients
    active_leads = Lead.objects.filter(
        team=team,
        is_deleted=False,
        converted_to_client=False
    )
    
    active_clients = Client.objects.filter(
        team=team,
        is_deleted=False
    )
    
    # Calculate lead statistics for active leads only
    lead_stats = {
        'total': active_leads.count(),
        'new': active_leads.filter(status='new').count(),
        'contacted': active_leads.filter(status='contacted').count(),
        'under_negotiation': active_leads.filter(status='under negotiation').count(),
        'won': active_leads.filter(status='won').count(),
        'lost': active_leads.filter(status='lost').count(),
    }
    
    # Get upcoming activities for active leads only
    lead_activities = Activity.objects.filter(
        lead__team=team,
        lead__is_deleted=False,
        lead__converted_to_client=False,
        date__gte=timezone.now().date()
    ).order_by('date', 'time')[:5]
    
    # Get activity counts for active leads
    activity_counts = Activity.objects.filter(
        lead__team=team,
        lead__is_deleted=False,
        lead__converted_to_client=False,
        date__gte=timezone.now().date()
    ).values('activity_type').annotate(count=Count('id'))
    
    context = {
        'leads': active_leads,
        'clients': active_clients,
        'total_leads': lead_stats['total'],
        'total_clients': active_clients.count(),
        'lead_stats': lead_stats,
        'lead_activities': lead_activities,
        'activity_counts': activity_counts,
    }
    
    return render(request, 'dashboard/dashboard.html', context)