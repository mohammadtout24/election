from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

class Candidate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, 
                                verbose_name="Linked User Account", 
                                help_text="User account for the candidate to manage their profile.")
    
    name = models.CharField(max_length=100, default="Unknown Candidate")
    party = models.CharField(max_length=100, default="Independent")
    
    # KEY CHANGE: Use RichTextField instead of TextField
    description = RichTextField(blank=True, verbose_name="Biography/Bio", default="")
    
    image = models.ImageField(upload_to='candidates/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.party})"


class Vote(models.Model):
    candidate = models.ForeignKey('Candidate', on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # new
    session_key = models.CharField(max_length=40, unique=True, db_index=True)
    voted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vote for {self.candidate.name} ({self.voted_at.date()})"
