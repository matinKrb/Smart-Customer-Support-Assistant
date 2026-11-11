from django.db import models
from .embedding_model import embed_text

# Create your models here.

class KnowledgeItem(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    embedding = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        text_to_embed = f"{self.title}\n{self.content}"
        self.embedding = embed_text(text_to_embed)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Knowledge Item"
        verbose_name_plural = "Knowledge Items"