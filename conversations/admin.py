from django.contrib import admin
from django.urls import path , reverse
from django.utils.html import format_html
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages as django_messages
from conversations.telegram_client import send_message
from conversations.state_machine import transition_to
from conversations.models import Conversation, TelegramUpdate ,Message , AuditLog

class MessageInline(admin.StackedInline):
    model = Message
    extra = 0
    readonly_fields = ('sender', 'text', 'created_at')
    can_delete = False
    ordering = ['created_at']
# Register your models here.
@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    # inlines = [MessageInline]
    list_display = [ 'telegram_chat_id','status', 'uuid' ,'reply_link' ]
    list_filter = ['status']
    def reply_link(self , obj):
        url = reverse('admin:conversation_reply', args=[obj.uuid])
        return format_html('<a href="{}">پاسخ بده</a>', url)
    reply_link.short_description = "پاسخ سریع"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<uuid:conversation_id>/reply/',
                self.admin_site.admin_view(self.reply_view),
                name='conversation_reply',
            ),
        ]
        return custom_urls + urls

    def reply_view(self, request, conversation_id):
        conversation = get_object_or_404(Conversation, uuid=conversation_id)

        if request.method == 'POST':
            reply_text = request.POST.get('reply_text', '').strip()

            if reply_text:
                Message.objects.create(conversation=conversation, sender='human', text=reply_text)
                try:
                    send_message(chat_id=conversation.telegram_chat_id, text=reply_text)
                except Exception as e:
                    django_messages.error(request, f'پیام ذخیره شد ولی ارسال به تلگرام ناموفق بود: {e}')

                if conversation.status == Conversation.Status.WAITING_FOR_HUMAN:
                    transition_to(conversation, Conversation.Status.HUMAN_HANDLING)

                django_messages.success(request, "پاسخ با موفقیت ارسال شد.")
            else:
                django_messages.warning(request, "متن پاسخ نمی‌تواند خالی باشد.")

            return redirect('admin:conversations_conversation_change', conversation_id)

        return render(request, 'conversations/reply_form.html', {
            'conversation': conversation,
        })

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_filter = ['conversation']

@admin.register(TelegramUpdate)
class TelegramUpdateAdmin(admin.ModelAdmin):
    list_display = ['update_id']

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'event_type', 'created_at']
    list_filter = ['event_type']
    readonly_fields = ['conversation', 'event_type', 'details', 'created_at']

