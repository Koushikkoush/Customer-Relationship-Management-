from django.contrib.auth.models import User, Permission
from django.db import models
from team.models import Team
from django.db.models.signals import post_save
from django.dispatch import receiver

class Role(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('agent', 'Agent'),
        ('viewer', 'Viewer')
    ]
    
    name = models.CharField(max_length=20, choices=ROLE_CHOICES)
    team = models.ForeignKey(Team, related_name='roles', on_delete=models.CASCADE)
    permissions = models.ManyToManyField(Permission, blank=True)
    
    class Meta:
        unique_together = ['name', 'team']
    
    def __str__(self):
        return f"{self.get_name_display()} - {self.team.name}"

class Userprofile(models.Model):
    user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE)
    active_team = models.ForeignKey(Team, related_name='userprofiles', blank=True, null=True, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, related_name='users', null=True, blank=True, on_delete=models.SET_NULL)
    
    def get_active_team(self):
        if self.active_team:
            return self.active_team
        
        # Create a default team for the user if none exists
        team = Team.objects.filter(created_by=self.user).first()
        if not team:
            team = Team.objects.create(
                name=f"{self.user.username}'s Team",
                created_by=self.user
            )
            self.active_team = team
            self.save()
        
        return team


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Userprofile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()
