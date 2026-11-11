TOOLS_SCHEMA = [
    {
    "type": "function",
    "function": {
        "name": "get_order_status",
        "description": "دریافت وضعیت یک سفارش بر اساس شماره سفارش",
        "parameters": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "شماره سفارش مشتری"
                }
            },
            "required": ["order_id"]
        }
    }
    },
    {
        "type": "function",
        "function": {
            "name":"search_product",
            "description": "پیدا کردن یک محصول و دریافت وضعیت آن بر اساس عبارت سرچ شده ",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description":"عبارت جست و جو برای جست و جو در نام و توضیحات محصول"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": "ثبت تیکت ",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                        "description": "موضوع تیکت"
                    },
                    "description": {
                        "type": "string",
                        "description":"توضیحات و بدنه تیکت"
                    }
                },
                "required": ['subject', 'description']
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name":"request_human_handoff",
            "description": "واگذار کردن ادامه مکالمه به اپراتور پشتیبانی ",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description":"دلیل ارتباط با اپراتور پشتیبانی"
                    }
                },
                "required": ["reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge",
            "description": (
                "جست‌وجو در پایگاه دانش فروشگاه برای سؤالات عمومی و سیاست‌های کلی، "
                "مثل شرایط مرجوعی، گارانتی، زمان و شرایط ارسال، آدرس فروشگاه، و "
                "سایر سؤالات متداول. برای سؤالات مربوط به یک سفارش یا محصول خاص "
                "استفاده نشود."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "متن سؤال کاربر به همان زبانی که پرسیده"
                    }
                },
                "required": ["query"]
            }
        }
    },
]