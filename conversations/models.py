from django.db import models
import uuid

class Conversation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        WAITING_FOR_HUMAN = 'waiting_for_human', 'Waiting for Human'
        HUMAN_HANDLING = 'human_handling', 'Human Handling'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    telegram_chat_id = models.CharField(max_length=64 , db_index=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ACTIVE)
    consecutive_errors = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.telegram_chat_id} , STATUS : {self.status}'

    class Meta:
        verbose_name = 'conversation'
        verbose_name_plural = 'conversations'


class Message(models.Model):
    class Sender(models.TextChoices):
        CUSTOMER = 'customer', 'Customer'
        AI = 'ai', 'AI'
        HUMAN = 'human', 'Human Operator'
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
    sender = models.CharField(max_length=64 , choices=Sender.choices)
    text = models.TextField()
    tool_call_name = models.CharField(max_length=64 ,null=True ,blank=True)
    tool_call_payload = models.JSONField(null=True ,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = 'message'
        verbose_name_plural = 'messages'

    def __str__(self):
        return f'TEXT : {self.text[0:15]} , SENDER : {self.sender}'

class TelegramUpdate(models.Model):
    update_id = models.BigIntegerField(unique=True)
    received_at = models.DateTimeField(auto_now_add=True)


class AuditLog(models.Model):
    class EventType(models.TextChoices):
        HANDOFF_REQUESTED = 'handoff_requested', 'Handoff Requested'
        STATUS_CHANGED = 'status_changed', 'Status Changed'
        TOOL_CALLED = 'tool_called', 'Tool Called'

    conversation = models.ForeignKey(
        Conversation, related_name='audit_logs', on_delete=models.CASCADE
    )
    event_type = models.CharField(max_length=32, choices=EventType.choices)
    details = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type}  {self.conversation.uuid}"
