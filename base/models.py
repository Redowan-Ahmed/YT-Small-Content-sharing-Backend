from django.db import models
import uuid

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, db_index=True, default=uuid.uuid4, editable=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        abstract = True