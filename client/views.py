# import csv

# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from django.shortcuts import render, get_object_or_404, redirect

# from .forms import AddClientForm, AddCommentForm, AddFileForm
# from .models import Client

# from team.models import Team
    
# @login_required
# def clients_export(request):
#     team = request.user.userprofile.active_team
#     clients = team.clients.all()

#     response = HttpResponse(
#         content_type='text/csv',
#         headers={'Content-Disposition': 'attachment; filename="clients.csv"'},
#     )

#     writer = csv.writer(response)
#     writer.writerow(['Client', 'Description', 'Created at', 'Created by'])

#     for client in clients:
#         writer.writerow([client.name, client.description, client.created_at, client.created_by])
    
#     return response

# @login_required
# def clients_list(request):
#     team = request.user.userprofile.active_team
#     clients = team.clients.all()

#     return render(request, 'client/clients_list.html', {
#         'clients': clients
#     })

# @login_required
# def clients_add_file(request, pk):
#     if request.method == 'POST':
#         form = AddFileForm(request.POST, request.FILES)

#         if form.is_valid():
#             file = form.save(commit=False)
#             file.team = request.user.userprofile.get_active_team()
#             file.client_id = pk
#             file.created_by = request.user
#             file.save()

#             return redirect('clients:detail', pk=pk)
#     return redirect('clients:detail', pk=pk)

# @login_required
# def clients_detail(request, pk):
#     team = request.user.userprofile.active_team
#     client = get_object_or_404(team.clients, pk=pk)

#     if request.method == 'POST':
#         form = AddCommentForm(request.POST)

#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.team = request.user.userprofile.get_active_team()
#             comment.created_by = request.user
#             comment.client = client
#             comment.save()

#             return redirect('clients:detail', pk=pk)
#     else:
#         form = AddCommentForm()

#     return render(request, 'client/clients_detail.html', {
#         'client': client,
#         'form': form,
#         'fileform': AddFileForm(),
#     })

# @login_required
# def clients_add(request):
#     team = request.user.userprofile.get_active_team()

#     if request.method == 'POST':
#         form = AddClientForm(request.POST)

#         if form.is_valid():
#             client = form.save(commit=False)
#             client.created_by = request.user
#             client.team = team
#             client.save()

#             messages.success(request, 'The client was created.')

#             return redirect('clients:list')
#     else:
#         form = AddClientForm()

#     return render(request, 'client/clients_add.html', {
#         'form': form,
#         'team': team
#     })

# @login_required
# def clients_edit(request, pk):
#     team = request.user.userprofile.active_team
#     client = get_object_or_404(team.clients, pk=pk)

#     if request.method == 'POST':
#         form = AddClientForm(request.POST, instance=client)

#         if form.is_valid():
#             form.save()

#             messages.success(request, 'The changes was saved.')

#             return redirect('clients:list')
#     else:
#         form = AddClientForm(instance=client)
    
#     return render(request, 'client/clients_edit.html', {
#         'form': form
#     })

# @login_required
# def clients_delete(request, pk):
#     team = request.user.userprofile.active_team
#     client = get_object_or_404(team.clients, pk=pk)
#     client.delete()

#     messages.success(request, 'The client was deleted.')

#     return redirect('clients:list')

import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from .forms import AddClientForm, AddCommentForm, AddFileForm
from .models import Client

from team.models import Team

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
        'Client', 'Description', 'Service', 'Contact Person',
        'Min Cost', 'Max Cost', 'Approved Cost', 'GST/Service %', 'Final Cost',
        'Start Date', 'End Date', 'Working Days',
        'Created at', 'Created by'
    ])

    for client in clients:
        writer.writerow([
            client.name, client.description, 
            client.custom_service if client.service == 'Other' else client.service,
            client.contacted_person_name,
            client.min_cost, client.max_cost, client.approved_cost, 
            client.gst_service_percentage, client.final_cost,
            client.start_date, client.end_date, client.working_days,
            client.created_at, client.created_by
        ])
    
    return response

@login_required
def clients_list(request):
    team = request.user.userprofile.active_team
    clients = team.clients.all()

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
    team = request.user.userprofile.get_active_team()

    if request.method == 'POST':
        form = AddClientForm(request.POST)

        if form.is_valid():
            client = form.save(commit=False)
            client.created_by = request.user
            client.team = team
            client.save()

            messages.success(request, 'The client was created.')

            return redirect('clients:list')
        else:
            form = AddClientForm()

    return render(request, 'client/clients_add.html', {
        'form': form,
        'team': team
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
    clients = team.clients.all()
    notifications = []
    
    for client in clients:
        if client.end_date and not client.is_deleted:
            notifications.append({
                'id': client.id,
                'name': client.name,
                'end_date': client.end_date
            })
    
    return JsonResponse({'notifications': notifications})