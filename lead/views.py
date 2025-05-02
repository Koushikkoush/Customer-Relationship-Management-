from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView

from .forms import AddCommentForm, AddFileForm, AddLeadForm
from .models import Lead

# Uncomment this line
from client.models import Client, Comment as ClientComment
from team.models import Team
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required
def get_client_details(request):
    """
    AJAX view to retrieve client details
    """
    client_id = request.GET.get('client_id')
    print(f"Received request for client_id: {client_id}")  # Debug print
    
    try:
        client = Client.objects.get(id=client_id)
        print(f"Found client: {client.email}, {client.phone_number}")  # Debug print
        return JsonResponse({
            'success': True,
            'email': client.email,
            'phone_number': client.phone_number or '',
        })
    except Client.DoesNotExist:
        print(f"Client not found with id: {client_id}")  # Debug print
        return JsonResponse({
            'success': False,
            'message': 'Client not found'
        })


class LeadListView(LoginRequiredMixin, ListView):
    model = Lead
    
    def get_queryset(self):
        queryset = super(LeadListView, self).get_queryset()
        team = self.request.user.userprofile.active_team
        return queryset.filter(team=team, converted_to_client=False, is_deleted=False)


class LeadDetailView(LoginRequiredMixin, DetailView):
    model = Lead
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AddCommentForm()
        context['fileform'] = AddFileForm()

        return context

    def get_queryset(self):
        queryset = super(LeadDetailView, self).get_queryset()
        team = self.request.user.userprofile.active_team

        return queryset.filter(team=team, pk=self.kwargs.get('pk'))


class LeadDeleteView(LoginRequiredMixin, DeleteView):
    model = Lead
    success_url = reverse_lazy('leads:list')

    def get_queryset(self):
        queryset = super(LeadDeleteView, self).get_queryset()
        team = self.request.user.userprofile.active_team
        return queryset.filter(team=team, pk=self.kwargs.get('pk'))
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()  # Use soft delete instead of actual deletion
        messages.success(request, 'The lead was deleted successfully.')
        return HttpResponseRedirect(self.get_success_url())
    
    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def get(self, request, *args, **kwargs):
        messages.success(request, 'The lead was deleted successfully.')
        return self.post(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'The lead was deleted successfully.')
        return super().delete(request, *args, **kwargs)

class LeadUpdateView(LoginRequiredMixin, UpdateView):
    model = Lead
    fields = (
        'client_name', 
        'email', 
        'phone_number', 
        'description', 
        'priority', 
        'status',
        'service',  # Added service field
        'custom_service',  # Added custom service field
    )
    success_url = reverse_lazy('leads:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit lead'
        return context

    def get_queryset(self):
        queryset = super(LeadUpdateView, self).get_queryset()
        team = self.request.user.userprofile.active_team
        return queryset.filter(team=team, pk=self.kwargs.get('pk'))
    
    def form_valid(self, form):
        # Validate custom service if service is "Other"
        if form.cleaned_data.get('service') == 'Other' and not form.cleaned_data.get('custom_service'):
            form.add_error('custom_service', 'Please specify the custom service')
            return self.form_invalid(form)
            
        messages.success(self.request, 'The lead was updated successfully.')
        return super().form_valid(form)

class LeadCreateView(LoginRequiredMixin, CreateView):
    model = Lead
    form_class = AddLeadForm
    success_url = reverse_lazy('leads:list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team = self.request.user.userprofile.get_active_team()
        context['team'] = team
        context['title'] = 'Add lead'
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        
        # Validate custom service if service is "Other"
        if form.cleaned_data.get('service') == 'Other' and not form.cleaned_data.get('custom_service'):
            form.add_error('custom_service', 'Please specify the custom service')
            return self.form_invalid(form)
            
        self.object.created_by = self.request.user
        self.object.team = self.request.user.userprofile.get_active_team()
        self.object.save()
        messages.success(self.request, 'The lead was created successfully.')
        return redirect(self.get_success_url())

class AddFileView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        form = AddFileForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.save(commit=False)
            file.team = self.request.user.userprofile.get_active_team()
            file.lead_id = pk
            file.created_by = request.user
            file.save()
            messages.success(request, 'The file was added successfully.')
        else:
            messages.error(request, 'There was an error adding the file.')

        return redirect('leads:detail', pk=pk)

class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')

        form = AddCommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.team = self.request.user.userprofile.get_active_team()
            comment.created_by = request.user
            comment.lead_id = pk
            comment.save()
            messages.success(request, 'The comment was added successfully.')
        else:
            messages.error(request, 'There was an error adding the comment.')

        return redirect('leads:detail', pk=pk)

class ConvertToClientView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        team = self.request.user.userprofile.active_team
        lead = get_object_or_404(Lead, team=team, pk=pk)

        # Create new client using lead information
        client = Client.objects.create(
            name=f"Lead from {lead.client_name}",  # Use email as the client name
            email=lead.email,
            phone_number=lead.phone_number,
            description=lead.description,
            created_by=request.user,
            team=team,
        )

        lead.converted_to_client = True
        lead.save()

        # Convert lead comments to client comments
        for comment in lead.comments.all():
            ClientComment.objects.create(
                client=client,
                content=comment.content,
                created_by=comment.created_by,
                team=team
            )
        
        messages.success(request, 'The lead was converted to a client successfully.')
        return redirect('leads:list')


from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from .models import Lead, Activity

def schedule_activity(request, pk):
    if request.method == 'POST':
        lead = get_object_or_404(Lead, pk=pk)
        
        activity = Activity.objects.create(
            lead=lead,
            activity_type=request.POST.get('activity_type'),
            title=request.POST.get('title'),
            date=request.POST.get('activity_date'),
            time=request.POST.get('activity_time'),
            notes=request.POST.get('notes', '')
        )
        
        messages.success(request, 'Activity scheduled successfully!')
        return redirect('leads:detail', pk=pk)
    
    return redirect('leads:list')