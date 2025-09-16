from django.db import models
import uuid

# Create your models here.
class User(models.Model):
   id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
   name = models.CharField(max_length=100, null=False, default="")
   last_name = models.CharField(max_length=100, null=False, default="")
   email = models.EmailField(max_length=100, unique=True, null=False, default="")
   password = models.CharField(max_length=100, null=False, default="")
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)

   def __str__(self):
      return f"{self.name} - {self.last_name} - {self.email} - {self.created_at} - {self.updated_at}"
