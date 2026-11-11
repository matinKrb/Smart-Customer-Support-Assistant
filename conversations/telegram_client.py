import requests
from django.conf import settings

TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"
# def _get_proxies():
#     if settings.TELEGRAM_PROXY_URL:
#         return {
#             "http": settings.TELEGRAM_PROXY_URL,
#             "https": settings.TELEGRAM_PROXY_URL,
#         }
#     return None


def send_message(chat_id : str , text : str) -> dict:
    url = f"{TELEGRAM_API_URL}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": text,
    }
    response = requests.post(
        url,
        json=params ,
        timeout=10,
        # proxies=_get_proxies(),
    )
    if not response.ok:
        print("TELEGRAM ERROR BODY:", response.text)
    response.raise_for_status()
    return response.json()