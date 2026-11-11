from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from rest_framework import status
import json
import logging
from .models import Conversation , Message , TelegramUpdate
from .telegram_client import send_message
from agent.core import run_agent
logger = logging.getLogger('telegram_webhook')

MAX_CONSECUTIVE_ERRORS = 3
# Create your views here.
@csrf_exempt
@require_POST
def telegram_webhook(request , secret : str):
    if secret != settings.TELEGRAM_WEBHOOK_SECRET:
        logger.warning("Webhook called with invalid secret")
        return JsonResponse( {'ok' : False} ,status=status.HTTP_403_FORBIDDEN)

    body = json.loads(request.body.decode('utf-8'))
    update_id = body.get('update_id')
    if update_id is not None:
        _, created = TelegramUpdate.objects.get_or_create(update_id=update_id)
        if not created:
            logger.info(f"Duplicate update_id={update_id} ignored")
            return JsonResponse( {'ok' : True})


    message = body.get('message')
    if message is None:
        logger.info("Update without 'message' field, ignored")
        return JsonResponse({'ok': True})

    message_text = message.get('text')
    chat_id = str(message.get('chat').get('id'))

    con, created2 = Conversation.objects.get_or_create(telegram_chat_id=chat_id)
    if not isinstance(message_text, str):
        logger.info("Non-text message received, ignored")
        # return JsonResponse({'ok' : True})
        reply_text = 'این ایجنت فقط از پیام متنی پشتیبانی میکند.'
    else:
        Message.objects.create(conversation=con, sender=Message.Sender.CUSTOMER, text=message_text)

        if con.status in [Conversation.Status.HUMAN_HANDLING]:
            logger.info(f"conversation_id={con.uuid} is in human mode, skipping AI response")
            return JsonResponse({'ok': True})

        try:
            reply_text = run_agent(con, message_text)
            con.consecutive_errors = 0
            con.save(update_fields=['consecutive_errors'])
        except Exception as e:
            logger.error(f"Agent failed for conversation_id={con.uuid}: {e}")
            con.consecutive_errors += 1
            con.save(update_fields=['consecutive_errors'])

            if con.consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                from .state_machine import transition_to
                transition_to(con, Conversation.Status.WAITING_FOR_HUMAN, reason="خطای مکرر Agent")
                reply_text = "متأسفانه در پردازش درخواست شما مشکلی پیش اومد. درخواستتون برای یک کارشناس ارسال شد."
            else:
                reply_text = "متأسفانه در پردازش درخواست شما مشکلی پیش اومد. لطفاً دوباره امتحان کنید."

    logger.info(f"conversation_id={con.uuid} sending reply")

    result = send_message(chat_id=chat_id , text=reply_text)
    logger.debug(f"Telegram API response: {result}")
    Message.objects.create(conversation=con, sender=Message.Sender.AI , text=reply_text)
    return JsonResponse({'ok' : True})