# Smart Customer Support Assistant / دستیار هوشمند پشتیبانی مشتریان

[فارسی](#فارسی) | [English](#english)

<div dir="rtl">

# دستیار هوشمند پشتیبانی مشتریان

یک دستیار هوشمند پشتیبانی برای فروشگاه‌های آنلاین که از طریق بات تلگرام کار می‌کند.

دستیار پیام مشتری را می‌فهمد و تصمیم می‌گیرد چه کاری انجام دهد: پاسخ از پایگاه دانش، فراخوانی یک ابزار کسب‌وکاری، پرسیدن سؤال تکمیلی، یا واگذاری مکالمه به اپراتور انسانی. پاسخ هم در همان چت تلگرام ارسال می‌شود.

> **وضعیت:** نسخه MVP. ساخته‌شده با Django، DRF و PostgreSQL.

## قابلیت‌ها

* **اتصال به تلگرام** از طریق Webhook، همراه با جلوگیری از پردازش تکراری پیام‌ها و یک کد مخفی در آدرس Webhook.

* **ایجنت مبتنی بر LLM با Tool Calling** (سرویس Groq با API سازگار با OpenAI). ایجنت اطلاعات سفارش، محصول و قوانین را از خودش نمی‌سازد و از ابزارها می‌گیرد.

* **پایگاه دانش با RAG** برای سؤالات متداول (مرجوعی، گارانتی، ارسال، آدرس فروشگاه). Embedding ها به‌صورت محلی با `sentence-transformers` ساخته می‌شوند و به هیچ API بیرونی نیاز نیست.

* **واگذاری به اپراتور** با یک ماشین حالت (State Machine) برای مکالمه. بعد از واگذاری، ربات تا زمانی که اپراتور مکالمه را برنگرداند پاسخ نمی‌دهد.

* **پاسخ اپراتور از پنل ادمین Django:** اپراتور تاریخچه کامل را می‌بیند و بدون خروج از پنل، پاسخ را در تلگرام برای مشتری می‌فرستد.

* **API مدیریتی با JWT** برای مکالمات، آیتم‌های دانش و آمار کلی.

* **Audit Log** برای تغییر وضعیت‌ها و رویدادهای واگذاری.

* **مدیریت خطا:** خطای LLM یا ابزارها باعث از کار افتادن مکالمه نمی‌شود. بعد از چند خطای پشت‌سرهم، مکالمه به انسان واگذار می‌شود.

## نحوه کار

```
Telegram  ->  Webhook (ویوی Django)  ->  Conversation / Message (PostgreSQL)
                                              |
                                              v
                                        Agent (run_agent)
                                  /        |          \         \
                        وضعیت سفارش    جست‌وجوی      جست‌وجو در     واگذاری به انسان /
                                        محصول       پایگاه دانش     ثبت تیکت
                                                       (RAG)

```

1. تلگرام پیام را به Webhook می‌فرستد.

2. پیام ذخیره می‌شود. اگر مکالمه در وضعیت انسانی باشد، ربات پاسخ نمی‌دهد.

3. در غیر این صورت، ایجنت Context را می‌سازد (پرامپت سیستمی + چند پیام آخر)، LLM را همراه با Schema ابزارها صدا می‌زند، ابزار درخواستی را اجرا می‌کند، نتیجه را به مدل برمی‌گرداند و این چرخه را تا گرفتن پاسخ نهایی ادامه می‌دهد.

4. پاسخ به تلگرام ارسال و ذخیره می‌شود.

### وضعیت‌های مکالمه

| وضعیت | معنی | 
| ----- | ----- | 
| `active` | ایجنت به‌صورت خودکار پاسخ می‌دهد | 
| `waiting_for_human` | درخواست واگذاری ثبت شده، هنوز اپراتوری پاسخ نداده | 
| `human_handling` | اپراتور در حال رسیدگی است | 
| `resolved` | حل‌شده | 
| `closed` | وضعیت نهایی | 

> گذارهای مجاز در `conversations/state_machine.py` تعریف شده‌اند.

### ابزارهای ایجنت

| ابزار | کاربرد | 
| ----- | ----- | 
| `get_order_status` | وضعیت سفارش با شماره سفارش | 
| `search_product` | جست‌وجوی محصول و وضعیت موجودی | 
| `create_support_ticket` | ثبت تیکت پشتیبانی | 
| `request_human_handoff` | انتقال مکالمه به `waiting_for_human` | 
| `search_knowledge` | جست‌وجوی معنایی در پایگاه دانش (RAG) | 

> ابزارهای سفارش، محصول و تیکت در `agent/business_api.py` با داده‌های ساختگی (Mock) پیاده شده‌اند. برای استفاده واقعی، آن‌ها را با فراخوانی API فروشگاه خودتان جایگزین کنید.

## پشته فناوری

| لایه | فناوری | 
| ----- | ----- | 
| Backend | Python، Django، Django REST Framework | 
| پایگاه داده | PostgreSQL | 
| مدل زبانی | Groq (`openai/gpt-oss-120b`) | 
| Embedding | `sentence-transformers` (مدل `paraphrase-multilingual-MiniLM-L12-v2`)، اجرای محلی | 
| احراز هویت API مدیریتی | JWT (`djangorestframework-simplejwt`) | 
| کانال ارتباطی | Telegram Bot API | 

## ساختار پروژه

```
core/             تنظیمات پروژه Django و مسیرهای اصلی
conversations/    مدل‌های Conversation، Message و AuditLog، Webhook تلگرام،
                  ماشین حالت، ویوی پاسخ اپراتور، API مدیریتی
agent/            حلقه ایجنت، پرامپت سیستمی، Schema ابزارها، ابزارهای کسب‌وکاری
knowledge/        مدل KnowledgeItem، Embedding محلی، جست‌وجوی معنایی، API

```

## راه‌اندازی

### پیش‌نیازها

* Python 3.11 یا بالاتر

* PostgreSQL

* توکن بات تلگرام از [@BotFather](https://t.me/BotFather)

* کلید API سرویس Groq

* یک آدرس عمومی HTTPS برای Webhook (در توسعه محلی از تونل‌هایی مثل ngrok، localtunnel یا Cloudflare Tunnel استفاده کنید)

### نصب

```bash
git clone <your-repo-url>
cd <your-repo-folder>

python -m venv venv
# لینوکس / مک
source venv/bin/activate
# ویندوز
venv\Scripts\activate

pip install -r requirements.txt
```

### پایگاه داده

یک دیتابیس PostgreSQL بسازید، مثلاً:

```sql
CREATE DATABASE ai_agent_db;
```

### متغیرهای محیطی

یک فایل `.env` در ریشه پروژه بسازید و هرگز آن را commit نکنید.

```env
SECRET_KEY=change-me
DEBUG=True

DB_NAME=ai_agent_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_SECRET=a-long-random-string
# اختیاری: فقط اگر از شبکه شما مستقیم به تلگرام دسترسی ندارید
# TELEGRAM_PROXY_URL=socks5h://127.0.0.1:10808

GROQ_API_KEY=your-groq-api-key
```

> اگر از پراکسی SOCKS استفاده می‌کنید، پکیج `requests[socks]` را هم نصب کنید.

### اجرا

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

> اولین باری که یک آیتم دانش ذخیره شود، مدل Embedding از Hugging Face دانلود می‌شود. بعد از آن، کاملاً آفلاین کار می‌کند.

### ثبت Webhook تلگرام

سرور محلی را با یک تونل در دسترس قرار دهید (مثلاً `ngrok http 8000`) و سپس:

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://<your-public-url>/api/telegram/webhook/<TELEGRAM_WEBHOOK_SECRET>/"
```

با `getWebhookInfo` می‌توانید وضعیت را بررسی کنید. اگر آدرس تونل عوض شد، باید Webhook را دوباره ثبت کنید.

### افزودن دانش

وارد `/admin/` شوید، به بخش **Knowledge Items** بروید و سؤالات متداول فروشگاه را وارد کنید (مرجوعی، گارانتی، ارسال، آدرس فروشگاه). Embedding هنگام ذخیره به‌صورت خودکار ساخته می‌شود. محتوا را به همان زبانی بنویسید که مشتری‌ها سؤال می‌پرسند. نوشتن چند عبارت رایج برای یک موضوع، دقت جست‌وجو را بالاتر می‌برد.

## API مدیریتی

همه مسیرهای زیر به توکن دسترسی JWT نیاز دارند.

| مسیر | متد | توضیح | 
| ----- | ----- | ----- | 
| `/api/token/` | POST | دریافت توکن دسترسی و Refresh | 
| `/api/token/refresh/` | POST | تمدید توکن دسترسی | 
| `/api/admin/conversations/` | GET | فهرست مکالمات | 
| `/api/admin/conversations/<uuid>/` | GET | جزئیات مکالمه همراه با پیام‌ها | 
| `/api/admin/knowledge-items/` | GET, POST, PUT, PATCH, DELETE | مدیریت آیتم‌های دانش | 
| `/api/admin/dashboard-stats/` | GET | مجموع مکالمات، تعداد واگذاری‌ها و خطاها | 

**نمونه فراخوانی:**

```bash
# گرفتن توکن
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

# فراخوانی API
curl http://127.0.0.1:8000/api/admin/conversations/ \
  -H "Authorization: Bearer <access-token>"
```

## روند کار اپراتور

1. مشتری درخواست صحبت با انسان می‌دهد یا ایجنت خودش مکالمه را واگذار می‌کند. وضعیت مکالمه می‌شود `waiting_for_human`.

2. در `/admin/` به بخش **Conversations** بروید و روی لینک پاسخ همان مکالمه بزنید.

3. با اولین پاسخ شما وضعیت به `human_handling` تغییر می‌کند و ربات ساکت می‌ماند.

4. بعد از پایان کار، با Action های پنل ادمین مکالمه را به `active` برگردانید (فعال شدن دوباره AI) یا حل‌شده علامت بزنید.

## تست

```bash
python manage.py test
```

سرویس‌های بیرونی (تلگرام و LLM) در تست‌ها Mock می‌شوند، پس بدون اینترنت هم اجرا می‌شوند.

## نکات امنیتی

* کلیدها و توکن‌ها از متغیرهای محیطی خوانده می‌شوند و داخل سورس کد نیستند.

* آدرس Webhook شامل یک کد مخفی است و درخواست با کد اشتباه رد می‌شود.

* پیام‌های تکراری تلگرام با `update_id` نادیده گرفته می‌شوند.

* مسیرهای API مدیریتی به احراز هویت JWT نیاز دارند.

* پرامپت سیستمی به ایجنت دستور می‌دهد تلاش برای تغییر دستورالعمل‌ها را رد کند و فقط به سؤالات مرتبط با فروشگاه پاسخ دهد. این یک محافظت در سطح پرامپت است، نه دفاع کامل در برابر Prompt Injection. برای محیط واقعی، اعتبارسنجی ورودی یا یک Classifier جداگانه قبل از LLM اضافه کنید.

* در محیط واقعی `DEBUG=False` بگذارید و `ALLOWED_HOSTS` را محدود کنید.

## محدودیت‌های شناخته‌شده

* ابزارهای سفارش، محصول و تیکت پیاده‌سازی ساختگی (Mock) هستند؛ جهت پیاده‌سازی و اتصال واقعی پروژه به یک فروشگاه آنلاین، نیاز به فراخوانی و پیاده‌سازی APIهای اختصاصی آن فروشگاه می‌باشد.

* جست‌وجوی معنایی یک پیمایش خطی روی همه آیتم‌های فعال است که برای پایگاه دانش کوچک کافی است. برای حجم بالا باید به یک Vector Database مهاجرت کرد.

* فقط پیام‌های متنی پردازش می‌شوند.

* فعلاً فقط تلگرام پشتیبانی می‌شود. کلاینت تلگرام در `conversations/telegram_client.py` جدا نگه داشته شده تا بتوان کانال دیگری را بدون بازنویسی ایجنت اضافه کرد.

</div>

---

# Smart Customer Support Assistant

An AI-powered customer support assistant for online stores operating via Telegram Bot. The agent understands customer messages and dynamically decides the best action: querying a knowledge base, invoking business tools, asking clarifying questions, or transferring the conversation to a human operator. Responses are delivered directly back to the Telegram chat.

> **Status:** MVP Version. Built with Django, Django REST Framework (DRF), and PostgreSQL.

## Features

* **Telegram Integration:** Webhook-based integration with duplicate message handling (`update_id`) and a secret path parameter for enhanced security.

* **LLM Agent with Tool Calling:** Powered by Groq API (OpenAI-compatible). Fetches accurate store information, orders, and policies without hallucinating.

* **RAG Knowledge Base:** Handles FAQs (returns, warranty, shipping, store address). Local embeddings generated via `sentence-transformers` without external API dependencies.

* **Human Handoff:** State Machine management. Once handed off, the bot stops automated responses until the operator releases the conversation back to AI.

* **Django Admin Operator Panel:** Operators can view full chat history and reply directly to Telegram from the admin panel without leaving Django.

* **Management API:** JWT-authenticated endpoints for managing conversations, knowledge items, and dashboard metrics.

* **Audit Logging & Error Resilience:** Logs all state transitions and handoff events. Consecutive LLM/tool failures automatically trigger human handoff.

## How It Works

```
Telegram  ->  Webhook (Django View)  ->  Conversation / Message (PostgreSQL)
                                              |
                                              v
                                        Agent (run_agent)
                                  /        |          \         \
                          Order Status   Product   Knowledge Base  Human Handoff /
                                         Search        (RAG)        Create Ticket

```

1. Telegram forwards the message to the Webhook.

2. The message is stored. If the conversation is currently handled by a human, the bot stays silent.

3. Otherwise, the Agent builds context (system prompt + recent messages), calls the LLM with tool schemas, executes requested tools, passes results back to the model, and repeats until a final response is generated.

4. The response is sent back to Telegram and saved in the database.

### Conversation States

| State | Description | 
| ----- | ----- | 
| `active` | Agent responds automatically | 
| `waiting_for_human` | Handoff requested, awaiting operator reply | 
| `human_handling` | Operator actively managing chat | 
| `resolved` | Issue resolved | 
| `closed` | Final closed status | 

> Allowed state transitions are defined in `conversations/state_machine.py`.

### Agent Tools

| Tool | Usage | 
| ----- | ----- | 
| `get_order_status` | Retrieve order status using order ID | 
| `search_product` | Search products and check inventory status | 
| `create_support_ticket` | Register a support ticket | 
| `request_human_handoff` | Transfer conversation to `waiting_for_human` | 
| `search_knowledge` | Semantic search in the Knowledge Base (RAG) | 

> Order, product, and ticket tools are mocked in `agent/business_api.py`. Replace them with your real e-commerce store API calls for production use.

## Tech Stack

| Layer | Technology | 
| ----- | ----- | 
| Backend | Python, Django, Django REST Framework | 
| Database | PostgreSQL | 
| LLM | Groq (`openai/gpt-oss-120b`) | 
| Embeddings | `sentence-transformers` (`paraphrase-multilingual-MiniLM-L12-v2`), local execution | 
| API Authentication | JWT (`djangorestframework-simplejwt`) | 
| Messaging Channel | Telegram Bot API | 

## Project Structure

```
core/             Django project configuration and root routing
conversations/    Conversation, Message, AuditLog models, Telegram Webhook,
                  State Machine, Operator response view, Management API
agent/            Agent loop, system prompt, tool schemas, business tools
knowledge/        KnowledgeItem model, local embeddings, semantic search, API

```

## Setup & Installation

### Prerequisites

* Python 3.11+

* PostgreSQL

* Telegram Bot Token from [@BotFather](https://t.me/BotFather)

* Groq API Key

* Public HTTPS URL for Webhook (for local dev, use ngrok, localtunnel, or Cloudflare Tunnel)

### Installation

```bash
git clone <your-repo-url>
cd <your-repo-folder>

python -m venv venv
# Linux / macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

pip install -r requirements.txt
```

### Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE ai_agent_db;
```

### Environment Variables (`.env`)

Create a `.env` file in the project root (never commit this file):

```env
SECRET_KEY=change-me
DEBUG=True

DB_NAME=ai_agent_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_WEBHOOK_SECRET=a-long-random-string
# Optional: Only if Telegram is blocked on your local network
# TELEGRAM_PROXY_URL=socks5h://127.0.0.1:10808

GROQ_API_KEY=your-groq-api-key
```

> If using a SOCKS proxy, also install `requests[socks]`.

### Running the Project

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

> The first time a knowledge item is saved, the Embedding model will download from Hugging Face. Subsequent runs operate completely offline.

### Registering Telegram Webhook

Expose your local server via a tunnel (e.g., `ngrok http 8000`) and run:

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://<your-public-url>/api/telegram/webhook/<TELEGRAM_WEBHOOK_SECRET>/"
```

Use `getWebhookInfo` to verify status. If your tunnel URL changes, re-register the Webhook.

### Adding Knowledge

Go to `/admin/`, open **Knowledge Items**, and enter your store FAQs (returns, warranty, shipping, address). Embeddings are generated automatically upon saving. Write content in the language customers ask questions in for best results.

## Management API

All endpoints below require a valid JWT access token.

| Path | Method | Description | 
| ----- | ----- | ----- | 
| `/api/token/` | POST | Obtain access and refresh tokens | 
| `/api/token/refresh/` | POST | Refresh access token | 
| `/api/admin/conversations/` | GET | List conversations | 
| `/api/admin/conversations/<uuid>/` | GET | Conversation details with message history | 
| `/api/admin/knowledge-items/` | GET, POST, PUT, PATCH, DELETE | Manage knowledge items | 
| `/api/admin/dashboard-stats/` | GET | Total conversations, handoffs, and error stats | 

**Example API Usage:**

```bash
# Obtain Token
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

# Call API
curl http://127.0.0.1:8000/api/admin/conversations/ \
  -H "Authorization: Bearer <access-token>"
```

## Operator Workflow

1. Customer requests a human operator or the agent automatically triggers handoff. State changes to `waiting_for_human`.

2. Go to `/admin/`, navigate to **Conversations**, and click the reply link for that chat.

3. On your first reply, state updates to `human_handling` and the bot remains silent.

4. Once finished, use Admin Panel Actions to switch state back to `active` (re-enabling AI) or mark as `resolved`.

## Testing

```bash
python manage.py test
```

External services (Telegram and LLM) are mocked during tests, allowing them to run offline.

## Security Notes

* Keys and tokens are loaded strictly from environment variables.

* Webhook URL contains a secret key; unauthorized requests are rejected.

* Duplicate Telegram messages are ignored using `update_id`.

* Management API routes require JWT authentication.

* System prompt instructs the agent to ignore prompt injection attempts and restrict answers to store topics. For production, add input validation or a safety classifier layer.

* Set `DEBUG=False` and restrict `ALLOWED_HOSTS` in production.

## Known Limitations

* Order, product, and ticket APIs are mock implementations; actual production deployment on a store requires integration with the specific store's backend APIs.

* Semantic search does a linear scan over active items (suitable for small KBs; migrate to a Vector DB for high volume).

* Text messages only.

* Only Telegram is currently integrated (Telegram client is decoupled in `conversations/telegram_client.py` to allow multi-channel expansion).