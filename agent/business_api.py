import random
from conversations.models import Conversation
from conversations.state_machine import transition_to

Products = [
    {'name':'s25 fe' , 'price':'170,000,000 toman' , 'Stock Status':'کالا موجود میباشد.'},
    {'name':'iphone 17 pro' , 'price':'400,000,000 toman' , 'Stock Status':' کالا موجود میباشد.'},
    {'name':'lenovo loq 2024' , 'price':'350,000,000 toman' , 'Stock Status':'موجودی به اتمام رسیده است.'},
    {'name':'ps5 pro' , 'price':'120,000,000 toman' , 'Stock Status':'موجودی به اتمام رسیده است.'},
]
Orders = [
    {'order_id':'4251' , 'customer_id' : '6547' , 'status' : 'در حال ارسال' },
    { 'order_id':'5698' , 'customer_id' : '2574' , 'status' : 'در حال آماده سازی' },
    { 'order_id':'7459' , 'customer_id' : '3547' , 'status' : 'به مقصد رسیده' },
]
Tickets = []

def get_order_status(order_id: str, customer_id: str = None) -> dict:
    for order in Orders:
        if order['order_id'] == order_id:
            return order
    return {"error": "سفارش پیدا نشد."}

def search_product(query: str) -> dict:
    normalized_query = query.strip().lower()

    for product in Products:
        normalized_name = product['name'].strip().lower()
        if normalized_query in normalized_name or normalized_name in normalized_query:
            return product

    query_words = set(normalized_query.split())
    for product in Products:
        product_words = set(product['name'].strip().lower().split())
        if query_words & product_words:
            return product

    return {'error': 'محصول مورد نظر پیدا نشد.'}

def create_support_ticket(subject: str, description: str)-> dict:
    Tickets.append({'subject': subject, 'description': description , 'ticketId':random.randint(100000,999999)})
    print(Tickets)
    for ticket in Tickets:
        if ticket['subject'] == subject:
            return {'Ticket id': ticket['ticketId']}
    return {'error':'ثبت تیکت با مشکل مواجه شد لطفا دوباره تلاش کنید.'}

def request_human_handoff(conversation_id: str, reason: str) -> dict:
    try:
        conversation = Conversation.objects.get(uuid=conversation_id)
    except Conversation.DoesNotExist:
        return {"error": "مکالمه پیدا نشد"}

    success = transition_to(
        conversation,
        Conversation.Status.WAITING_FOR_HUMAN,
        reason=reason,
    )

    if success:
        return {
            "status": "handoff_requested",
            "message": "درخواست شما برای یک کارشناس ارسال شد.",
        }
    else:
        return {
            "status": "already_in_human_mode",
            "message": "این مکالمه از قبل در حال بررسی توسط کارشناس است.",
        }