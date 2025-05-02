

import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from .forms import AddClientForm, AddCommentForm, AddFileForm
from .models import Client

from team.models import Team
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from .models import Client
from lead.models import Activity

@login_required
def clients_export(request):
    team = request.user.userprofile.active_team
    clients = team.clients.all()

    response = HttpResponse(
        content_type='text/csv',
        headers={'Content-Disposition': 'attachment; filename="clients.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow([
        'Client Name', 'Description', 'Service Type', 'Custom Service',
        'Contact Person', 'Email', 'Phone Number',
        'Min Cost (₹)', 'Max Cost (₹)', 'Approved Cost (₹)', 
        'GST/Service %', 'Final Cost (₹)',
        'Start Date', 'End Date', 'Working Days',
        'Created Date', 'Created By', 'Team'
    ])

    for client in clients:
        # Format dates
        start_date = client.start_date.strftime('%d-%m-%Y') if client.start_date else 'Not Set'
        end_date = client.end_date.strftime('%d-%m-%Y') if client.end_date else 'Not Set'
        created_date = client.created_at.strftime('%d-%m-%Y %H:%M')

        # Format costs with currency symbol
        min_cost = f"₹{client.min_cost:,.2f}" if client.min_cost else '₹0.00'
        max_cost = f"₹{client.max_cost:,.2f}" if client.max_cost else '₹0.00'
        approved_cost = f"₹{client.approved_cost:,.2f}" if client.approved_cost else '₹0.00'
        final_cost = f"₹{client.final_cost:,.2f}" if client.final_cost else '₹0.00'

        # Format GST percentage
        gst_percentage = f"{client.gst_service_percentage}%" if client.gst_service_percentage else '0%'

        writer.writerow([
            client.name or 'Not Provided',
            client.description or 'No Description',
            client.service or 'Not Specified',
            client.custom_service if client.service == 'Other' else 'N/A',
            client.contacted_person_name or 'Not Provided',
            client.email or 'No Email',
            client.phone_number or 'No Phone',
            min_cost,
            max_cost,
            approved_cost,
            gst_percentage,
            final_cost,
            start_date,
            end_date,
            client.working_days or 0,
            created_date,
            client.created_by.get_full_name() or client.created_by.username,
            team.name
        ])
    
    return response

@login_required
def clients_list(request):
    team = request.user.userprofile.active_team
    clients = team.clients.all()

    # Apply filters
    name_query = request.GET.get('name', '')
    email_query = request.GET.get('email', '')
    service_query = request.GET.get('service', '')
    date_filter = request.GET.get('date_filter', '')

    if name_query:
        clients = clients.filter(name__icontains=name_query)
    
    if email_query:
        clients = clients.filter(email__icontains=email_query)
    
    if service_query:
        clients = clients.filter(service=service_query)

    # Date filtering
    from datetime import datetime, timedelta
    today = datetime.now().date()
    
    if date_filter == 'today':
        clients = clients.filter(created_at__date=today)
    elif date_filter == 'week':
        week_ago = today - timedelta(days=7)
        clients = clients.filter(created_at__date__gte=week_ago)
    elif date_filter == 'month':
        month_ago = today - timedelta(days=30)
        clients = clients.filter(created_at__date__gte=month_ago)

    return render(request, 'client/clients_list.html', {
        'clients': clients
    })

@login_required
def clients_add_file(request, pk):
    if request.method == 'POST':
        form = AddFileForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.save(commit=False)
            file.team = request.user.userprofile.get_active_team()
            file.client_id = pk
            file.created_by = request.user
            file.save()

            # Create an automatic comment about the file upload with the user's comment
            comment_text = f"File uploaded: {file.file.name.split('/')[-1]}"
            if file.comment:
                comment_text += f"\nComment: {file.comment}"

            from .models import Comment
            Comment.objects.create(
                client_id=pk,
                content=comment_text,
                team=file.team,
                created_by=request.user
            )

            messages.success(request, 'File uploaded successfully.')
            return redirect('clients:detail', pk=pk)
    return redirect('clients:detail', pk=pk)

@login_required
def clients_detail(request, pk):
    team = request.user.userprofile.active_team
    client = get_object_or_404(team.clients, pk=pk)

    if request.method == 'POST':
        form = AddCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.team = request.user.userprofile.get_active_team()
            comment.created_by = request.user
            comment.client = client
            comment.save()

            return redirect('clients:detail', pk=pk)
    else:
        form = AddCommentForm()

    return render(request, 'client/clients_detail.html', {
        'client': client,
        'form': form,
        'fileform': AddFileForm(),
    })

@login_required
def clients_add(request):
    if request.method == 'POST':
        form = AddClientForm(request.POST)
        
        if form.is_valid():
            client = form.save(commit=False)
            client.team = request.user.userprofile.active_team
            client.created_by = request.user
            client.save()
            
            return redirect('clients:list')
    else:
        form = AddClientForm()
    
    return render(request, 'client/clients_add.html', {
        'form': form
    })

@login_required
def clients_edit(request, pk):
    team = request.user.userprofile.active_team
    client = get_object_or_404(team.clients, pk=pk)

    if request.method == 'POST':
        form = AddClientForm(request.POST, instance=client)

        if form.is_valid():
            form.save()

            messages.success(request, 'The changes were saved.')

            return redirect('clients:list')
    else:
        # Pre-populate the cost_range field
        initial_data = {}
        if client.min_cost is not None and client.max_cost is not None:
            initial_data['cost_range'] = f"{client.min_cost}-{client.max_cost}"
            
        form = AddClientForm(instance=client, initial=initial_data)
    
    return render(request, 'client/clients_edit.html', {
        'form': form
    })

@login_required
def clients_delete(request, pk):
    team = request.user.userprofile.active_team
    client = get_object_or_404(team.clients, pk=pk)
    client.delete()

    messages.success(request, 'The client was deleted.')

    return redirect('clients:list')

@login_required
def recalculate_costs(request, pk):
    """Recalculate the final cost based on approved cost and GST percentage"""
    team = request.user.userprofile.active_team
    client = get_object_or_404(team.clients, pk=pk)
    
    if client.approved_cost and client.gst_service_percentage:
        gst_amount = client.approved_cost * (client.gst_service_percentage / 100)
        client.final_cost = client.approved_cost + gst_amount
        client.save()
        
        messages.success(request, 'Final cost recalculated successfully.')
    else:
        messages.error(request, 'Both approved cost and GST percentage are required for calculation.')
    
    return redirect('clients:detail', pk=pk)


@login_required
def get_notifications(request):
    team = request.user.userprofile.active_team
    today = timezone.now().date()
    
    # Get upcoming activities - using lead__team instead of team
    activities = Activity.objects.filter(
        lead__team=team,
        date__gte=today,
        date__lte=today + timedelta(days=5)
    ).order_by('date')
    
    # Get clients with upcoming end dates
    clients = Client.objects.filter(
        team=team,
        end_date__isnull=False,
        end_date__gte=today,
        end_date__lte=today + timedelta(days=5)
    ).order_by('end_date')
    
    notifications = []
    
    # Add activity notifications - using lead.email instead of lead.name
    for activity in activities:
        days_until = (activity.date - today).days
        notifications.append({
            'name': activity.title,
            'message': f"Activity for {activity.lead.email if activity.lead else 'Unknown Lead'}",
            'days_remaining': days_until,
            'type': 'activity',
            'due_date': activity.date.strftime('%Y-%m-%d')
        })
    
    # Add client notifications
    for client in clients:
        days_until = (client.end_date - today).days
        notifications.append({
            'name': client.name,
            'message': 'Contract ending soon',
            'days_remaining': days_until,
            'type': 'client',
            'end_date': client.end_date.strftime('%Y-%m-%d')
        })
    
    return JsonResponse({
        'notifications': sorted(notifications, key=lambda x: x['days_remaining'])
    })