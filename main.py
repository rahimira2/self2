import os
import sys
import shutil
import subprocess
import asyncio
import json
import random
import aiohttp
import psutil
from pyrogram import Client, idle, filters, enums
from pyrogram.types import Message
from pyrogram.raw import functions, types
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone
from datetime import datetime
from hurry.filesize import size
from time import sleep
from pyrogram.enums import ParseMode, ChatType
from pyrogram.errors import PeerIdInvalid, UserIsBlocked
from pyrogram.enums import ChatMembersFilter
from pytz import timezone
from datetime import datetime
from plugins import is_installed, create_time, read_json, write_json

# ========== تنظیمات ادمین ==========
ADMIN_IDS = [5994044255, 6041671747]

# ========== نصب kurigram و حذف pyrogram ==========
try:
    if is_installed("pyrogram"):
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "pyrogram", "-y"], check=True)
    if not is_installed("kurigram"):
        subprocess.run([sys.executable, "-m", "pip", "install", "kurigram"], check=True)
except subprocess.CalledProcessError as e:
    print(f"An error occurred during the installation or uninstallation: {e}")

# ========== تنظیم فایل تنظیمات ==========
if not os.path.isfile("Setting.json"):
    with open("Setting.json", "w") as f:
        json.dump({"timename": "off", "timebio": "off", "online": "off", "playing": "off", "typing": "off"}, f, indent=6)

api_id = 26418454
api_hash = '8f23d087ad6db0d5e02263e771087a0f'
app = Client("CodeCraftersTeam", api_id, api_hash)

data = read_json("Setting.json")

# ========== راهنمای ربات ==========
HELP_TEXT = """**Hi {mention} 👋🏻

➖➖➖➖➖➖➖➖➖
<b>دستورات اصلی:</b>
• راهنما: [`.help`] یا [`/help`]
• پینگ: [`.ping`] یا [`/ping`]
• وضعیت: [`.status`]
• وضعیت حریم خصوصی: [وضعیت حریم] یا [STATUS PRIVACY]
• جوک: [جوک]
• بیو: [بیو]
• قیمت طلا: [طلا]
• تاریخ امروز: [تاریخ] یا [date]
• آب‌وهوای شهر: [هوا تهران] یا [هواشناسی تهران]
• منشن ادمین: [تگ ادمین] | [منشن ادمین] | [tag admin] | [mention admin]

<b>تنظیمات هوشمند:</b>
• نام با ساعت: [`.timename on`] / [`.timename off`]
• بیو با ساعت: [`.timebio on`] / [`.timebio off`]
• آنلاین خودکار: [`.online on`] / [`.online off`]
• وضعیت Playing: [`.playing on`] / [`.playing off`]
• وضعیت Typing: [`.typing on`] / [`.typing off`]

<b>قابلیت‌های هوش مصنوعی:</b>
• پرسش از GPT: [`.gpt متن یا سوال شما`]

<b>مدیریت گروه و کانال:</b>
• پاکسازی گروه‌ها: [پاکسازی گروه]
• پاکسازی کانال‌ها: [پاکسازی کانال]

<b>ارسال و فوروارد گروهی:</b>
• ارسال به پیوی: [ارسال به پیوی متن دلخواه] یا ریپلای
• ارسال به گروه: [ارسال به گروه متن دلخواه] یا ریپلای
• ارسال به همه: [ارسال به همه متن دلخواه] یا ریپلای
• ارسال به مخاطبین: [ارسال به مخاطبین متن دلخواه] یا ریپلای
• فوروارد به پیوی/گروه/همه/مخاطبین: مشابه بالا با "فوروارد" و ریپلای

<b>مدیریت بلاک:</b>
• بلاک کاربر: [مسدود] یا [بلاک] (ریپلای یا پیوی)
• لیست بلاک‌شده‌ها: [لیست بلاک] یا [blocked list]
➖➖➖➖➖➖➖➖➖
Developed by @Mahdi_r86 | Channel: https://t.me/IIII_95_IIII
**"""
# ========== هندلر خاموش کردن ==========
@app.on_message(filters.text & filters.user(ADMIN_IDS))
async def offself_handler(client: Client, m: Message):
    if m.text and m.text.strip() == "خاموش کردن":
        await m.reply("✅ ربات در حال خاموش شدن و حذف نشست است...")
        await asyncio.sleep(1)
        try:
            await client.log_out()
        except Exception as e:
            print(f"Error in log_out: {e}")
        await asyncio.sleep(1)
        files_to_delete = [
            "time.txt",
            "Setting.json",
            "CodeCraftersTeam.session-journal",
            "CodeCraftersTeam.session"
        ]
        for f in files_to_delete:
            for _ in range(3):
                try:
                    if os.path.exists(f):
                        os.remove(f)
                    break
                except Exception as e:
                    print(f"Error removing {f}: {e}")
                    sleep(1)
        if os.path.exists("__pycache__") and os.path.isdir("__pycache__"):
            try:
                shutil.rmtree("__pycache__")
            except Exception as e:
                print(f"Error removing __pycache__: {e}")
        os._exit(0)

# ========== پروفایل و وضعیت ==========
def update_profile():
    current_time = datetime.now(timezone("Asia/Tehran")).strftime("%H:%M")
    if not os.path.isfile("time.txt") or open("time.txt").read().strip() != current_time:
        try:
            hey = create_time()
            if data.get("timebio") == "on":
                app.invoke(functions.account.UpdateProfile(about=f'فضولی شما در تایم {hey} ثبت شد'))
            if data.get("timename") == "on":
                app.invoke(functions.account.UpdateProfile(last_name=hey))
            with open("time.txt", "w") as f:
                f.write(current_time)
        except Exception as e:
            print(f"Error in update_profile: {e}")

def online():
    if data.get('online') == 'on':
        try:
            x = app.send_message("me", "Develop By : @Mahdi_r86\nChannel : https://t.me/IIII_95_IIII")
            sleep(2)
            app.delete_messages("me", x.id)
        except Exception as e:
            print(f"Error in online: {e}")

# ========== اکشن‌های گروه ==========
@app.on_message(~filters.me & ((filters.private & ~filters.bot) | (filters.mentioned & filters.group)))
async def Actions(app, message):
    actions = {
        'playing': enums.ChatAction.PLAYING,
        'typing': enums.ChatAction.TYPING
    }
    for key, action in actions.items():
        if data.get(key) == 'on':
            try:
                await app.send_chat_action(chat_id=message.chat.id, action=action)
            except Exception as e:
                print(f"Error in {key} action: {e}")

# ========== ذخیره و ارسال عکس‌های تایم‌دار ==========
@app.on_message(filters.photo, group=200)
async def onphoto(c: Client, m: Message):
    try:
        if m.photo.ttl_seconds:
            rand = random.randint(1, 999)
            local = f"downloads/aks-{rand}.png"
            await app.download_media(message=m, file_name=f"aks-{rand}.png")
            user_id = m.from_user.id if m.from_user else m.chat.id
            username = m.from_user.username if m.from_user and m.from_user.username else f"ID: {user_id}"
            await app.send_photo(
                chat_id="me",
                photo=local,
                caption=f"🔥 New timed image {m.photo.date} | time: {m.photo.ttl_seconds}s | User: @{username}"
            )
            os.remove(local)
    except Exception as e:
        print(f"An error occurred: {e}")

# ========== قابلیت GPT ==========
GPT_API_URL = "https://api.majidapi.ir/gpt/35"
GPT_TOKEN = "rm2jvmq1ohjkbyg:r6WBwXgljYwB2d6gZ075"

async def handle_gpt(message):
    if not message.text or not message.text.strip().startswith(".gpt"):
        return
    parts = message.text.strip().split(" ", 1)
    if len(parts) < 2 or not parts[1].strip():
        await message.edit_text(
            "❗ بعد از دستور <b>.gpt</b> سوال یا متن خود را وارد کنید.\nمثال:\n<code>.gpt بهترین خواننده ایران</code>",
            parse_mode=ParseMode.HTML
        )
        return
    q = parts[1].strip()
    params = {
        "q": q,
        "token": GPT_TOKEN
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(GPT_API_URL, params=params) as resp:
                data = await resp.json()
        if (
            isinstance(data, dict)
            and data.get("status") == 200
            and data.get("result")
        ):
            result = data["result"]
            msg = (
                "🤖 <b>پاسخ هوش مصنوعی:</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"{result}\n"
                "━━━━━━━━━━━━━━━━━━"
            )
            await message.edit_text(msg, parse_mode=ParseMode.HTML)
        else:
            await message.edit_text("❌ دریافت پاسخ موفق نبود.", parse_mode=ParseMode.HTML)
    except Exception as e:
        await message.edit_text(
            f"❌ خطا در دریافت یا اتصال به API:\n<code>{e}</code>",
            parse_mode=ParseMode.HTML
        )

# ========== هندلر دریافت و ارسال جوک ==========
JOKE_API_URL = "https://api.majidapi.ir/fun/joke"
JOKE_TOKEN = "rm2jvmq1ohjkbyg:r6WBwXgljYwB2d6gZ075"

async def handle_joke(message):
    if not message.text or not message.text.strip().startswith("جوک"):
        return False
    params = {"token": JOKE_TOKEN}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(JOKE_API_URL, params=params) as resp:
                data = await resp.json()
        if (
            isinstance(data, dict)
            and data.get("status") == 200
            and data.get("result")
        ):
            joke = data["result"]
            msg = (
                "🤣 <b>جوک خنده‌دار برات پیدا کردم:</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"<i>{joke}</i>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "🔄 برای دریافت جوک جدید دوباره بنویس: <b>جوک</b>"
            )
            await message.edit_text(msg, parse_mode=ParseMode.HTML)
        else:
            await message.edit_text("❌ دریافت جوک موفق نبود.", parse_mode=ParseMode.HTML)
        return True
    except Exception as e:
        await message.edit_text(
            f"❌ خطا در دریافت یا اتصال به API:\n<code>{e}</code>",
            parse_mode=ParseMode.HTML
        )
        return True

# ========== هندلر دریافت بیو ==========
BIO_API_URL = "https://api.majidapi.ir/fun/bio"
BIO_TOKEN = "rm2jvmq1ohjkbyg:r6WBwXgljYwB2d6gZ075"

async def handle_bio(message):
    if not message.text or not message.text.strip().startswith("بیو"):
        return False
    params = {"token": BIO_TOKEN}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(BIO_API_URL, params=params) as resp:
                data = await resp.json()
        if (
            isinstance(data, dict)
            and data.get("status") == 200
            and data.get("result")
        ):
            bio = data["result"]
            msg = (
                "📝 <b>بیو پیشنهادی:</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"<i>{bio}</i>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "<i>برای دریافت بیو جدید دوباره بنویس: بیو</i>"
            )
            await message.edit_text(msg, parse_mode=ParseMode.HTML)
        else:
            await message.edit_text("❌ دریافت بیو موفق نبود.", parse_mode=ParseMode.HTML)
        return True
    except Exception as e:
        await message.edit_text(
            f"❌ خطا در دریافت یا اتصال به API:\n<code>{e}</code>",
            parse_mode=ParseMode.HTML
        )
        return True

# ========== هندلر دریافت قیمت طلا ==========
TALA_API_URL = "https://api.majidapi.ir/price/gold"
TALA_API_TOKEN = "rm2jvmq1ohjkbyg:r6WBwXgljYwB2d6gZ075"

async def handle_tala_command(m):
    try:
        msg = await m.reply("⏳ در حال دریافت اطلاعات قیمت طلا ...")
        async with aiohttp.ClientSession() as session:
            async with session.get(TALA_API_URL, params={"token": TALA_API_TOKEN}) as resp:
                data = await resp.json()
        if not data or "result" not in data:
            await msg.edit("❌ دریافت اطلاعات ناموفق بود.", parse_mode=ParseMode.HTML)
            return True
        result = data["result"]
        text = "<b>🏅 قیمت لحظه‌ای طلا:</b>\n"
        if result.get("tala"):
            text += "\n<b>• طلای گرمی:</b>\n"
            for i in result["tala"]:
                text += (f"▫️ <b>{i['title']}</b>\n"
                         f"  💵 قیمت: <b>{i['price']}</b>\n"
                         f"  🔻 تغییر: <code>{i['change']}</code>\n"
                         f"  📉 کمترین: <code>{i['lowest']}</code> | 📈 بیشترین: <code>{i['highest']}</code>\n"
                         f"  🕒 {i['time']}\n"
                         "━━━\n")
        if result.get("mesghal"):
            text += "\n<b>• مثقال:</b>\n"
            for i in result["mesghal"]:
                text += (f"▫️ <b>{i['title']}</b>\n"
                         f"  💵 قیمت: <b>{i['price']}</b>\n"
                         f"  🔻 تغییر: <code>{i['change']}</code>\n"
                         f"  📉 کمترین: <code>{i['lowest']}</code> | 📈 بیشترین: <code>{i['highest']}</code>\n"
                         f"  🕒 {i['time']}\n"
                         "━━━\n")
        if result.get("abshode"):
            text += "\n<b>• آبشده:</b>\n"
            for i in result["abshode"]:
                text += (f"▫️ <b>{i['title']}</b>\n"
                         f"  💵 قیمت: <b>{i['price']}</b>\n"
                         f"  🔻 تغییر: <code>{i['change']}</code>\n"
                         f"  📉 کمترین: <code>{i['lowest']}</code> | 📈 بیشترین: <code>{i['highest']}</code>\n"
                         f"  🕒 {i['time']}\n"
                         "━━━\n")
        if len(text) > 4000:
            for i in range(0, len(text), 4000):
                await m.reply(text[i:i+4000], parse_mode=ParseMode.HTML)
            await msg.delete()
        else:
            await msg.edit(text, parse_mode=ParseMode.HTML)
        return True
    except Exception as e:
        await m.reply(f"❌ خطا: {e}")
        return True

# ========== هندلر منشن ادمین‌های گروه ==========
async def handle_tag_admin(client, m: Message):
    text = (m.text or "").strip().lower()
    commands = [
        "تگ ادمین",
        "منشن ادمین",
        "tag admin",
        "mention admin"
    ]
    if text not in commands:
        return False

    chat_type = getattr(m.chat, 'type', None)
    if hasattr(chat_type, "value"):
        chat_type = chat_type.value.lower()
    elif isinstance(chat_type, str):
        chat_type = chat_type.lower()
    else:
        chat_type = ""

    if chat_type not in ["group", "supergroup"]:
        await m.reply("این دستور فقط در گروه‌ها قابل استفاده است.")
        return True

    admins = []
    async for member in client.get_chat_members(m.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
        if not member.user.is_bot:
            admins.append(member.user)

    if not admins:
        await m.reply("هیچ ادمینی در این گروه پیدا نشد!")
        return True

    mention_text = "🟢 منشن ادمین‌های گروه:\n"
    for user in admins:
        name = user.first_name or ""
        if user.last_name:
            name += " " + user.last_name
        mention_text += f"• <a href='tg://user?id={user.id}'>{name}</a>\n"

    await m.reply(mention_text, quote=True, parse_mode=ParseMode.HTML)
    return True

# ========== وضعیت حریم خصوصی ==========
privacy_keys = [
    (types.InputPrivacyKeyPhoneNumber(), "شماره (phone)", "📱"),
    (types.InputPrivacyKeyStatusTimestamp(), "بازدید (seen)", "🕒"),
    (types.InputPrivacyKeyProfilePhoto(), "پروفایل (profile)", "🖼️"),
    (types.InputPrivacyKeyForwards(), "فوروارد (forward)", "🔁"),
    (types.InputPrivacyKeyPhoneCall(), "تماس (calls)", "📞"),
    (types.InputPrivacyKeyAddedByPhone(), "دعوت (invite)", "➕"),
    (types.InputPrivacyKeyVoiceMessages(), "ویس (voice)", "🎤"),
]

def privacy_to_text(rules):
    if not rules:
        return "نامشخص"
    if any(rule.__class__.__name__ == "PrivacyValueAllowAll" for rule in rules):
        return "همه"
    if any(rule.__class__.__name__ == "PrivacyValueDisallowAll" for rule in rules):
        return "هیچکس"
    if any(rule.__class__.__name__ == "PrivacyValueAllowContacts" for rule in rules):
        return "مخاطبین"
    return "سفارشی"

async def get_privacy_status(client):
    result = {}
    for key_obj, fa_name, emoji in privacy_keys:
        res = await client.invoke(functions.account.GetPrivacy(key=key_obj))
        result[fa_name] = privacy_to_text(res.rules)
    return result

def format_farsi(status):
    lines = [
        "┏━━━ وضعیت حریم خصوصی شما ━━━┓\n"
    ]
    for (_, fa_name, emoji) in privacy_keys:
        lines.append(f"{emoji} {fa_name}: {status.get(fa_name, 'نامشخص')}")
    lines.append("\n┗━━━━━━━━━━━━━━━━━━━━━━┛")
    return "\n".join(lines)

def format_english(status):
    english_names = [
        ("Phone", "📱"),
        ("Seen", "🕒"),
        ("Profile", "🖼️"),
        ("Forward", "🔁"),
        ("Calls", "📞"),
        ("Invite", "➕"),
        ("Voice", "🎤"),
    ]
    lines = [
        "┏━━━ Your Privacy Status ━━━┓\n"
    ]
    for ((_, fa_name, emoji), (en_name, _)) in zip(privacy_keys, english_names):
        lines.append(f"{emoji} {en_name}: {status.get(fa_name, 'Unknown')}")
    lines.append("\n┗━━━━━━━━━━━━━━━━━━┛")
    return "\n".join(lines)

fa_commands = ["وضعیت حریم"]
en_commands = ["STATUS PRIVACY"]

async def handle_privet(message):
    text = message.text.strip().upper()
    if text in [cmd.upper() for cmd in fa_commands]:
        status = await get_privacy_status(message._client)
        await message.edit_text(format_farsi(status))
        return True
    elif text in [cmd.upper() for cmd in en_commands]:
        status = await get_privacy_status(message._client)
        await message.edit_text(format_english(status))
        return True
    return False

# ========== سایر هندلرها (بلاک، لیست بلاک، ارسال گروهی و ...) را اینجا قرار بده ==========
# ====== پاکسازی گروه و کانال ======
RELOAD_FRAMES = [
    "⏳ منتظر بمانید...\n[░░░░░░░░░░]",
    "⏳ منتظر بمانید...\n[█░░░░░░░░░]",
    "⏳ منتظر بمانید...\n[██░░░░░░░░]",
    "⏳ منتظر بمانید...\n[███░░░░░░░]",
    "⏳ منتظر بمانید...\n[████░░░░░░]",
    "⏳ منتظر بمانید...\n[█████░░░░░]",
    "⏳ منتظر بمانید...\n[██████░░░░]",
    "⏳ منتظر بمانید...\n[███████░░░]",
    "⏳ منتظر بمانید...\n[████████░░]",
    "⏳ منتظر بمانید...\n[█████████░]",
    "⏳ منتظر بمانید...\n[██████████]",
    "✅ عملیات کامل شد!"
]

async def handle_delete_GROP(client, m):
    if m.text and m.text.strip() == "پاکسازی گروه":
        msg = await m.reply(RELOAD_FRAMES[0])
        for frame in RELOAD_FRAMES[1:]:
            await asyncio.sleep(0.3)
            await msg.edit(frame)
        deleted = 0
        group_ids = []
        async for dialog in client.get_dialogs():
            if dialog.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
                group_ids.append(dialog.chat.id)
        found = len(group_ids)
        for idx, group_id in enumerate(group_ids, 1):
            try:
                await client.leave_chat(group_id)
                deleted += 1
                await msg.edit(f"در حال ترک گروه {deleted} از {found} ...")
                await asyncio.sleep(0.2)
            except Exception as e:
                print(f"خطا در ترک گروه {group_id}: {e}")
        await msg.edit(
            f"✅ پاکسازی گروه‌ها تمام شد!\n"
            f"تعداد کل گروه‌ها: {found}\n"
            f"تعداد موفق ترک شده: {deleted}\n"
            f"{'تمام گروه‌ها ترک شدند.' if deleted==found else 'برخی گروه‌ها ترک نشدند.'}"
        )
        return True
    return False

async def handle_delete_CHANEL(client, m):
    if m.text and m.text.strip() == "پاکسازی کانال":
        msg = await m.reply(RELOAD_FRAMES[0])
        for frame in RELOAD_FRAMES[1:]:
            await asyncio.sleep(0.3)
            await msg.edit(frame)
        deleted = 0
        channel_ids = []
        async for dialog in client.get_dialogs():
            if dialog.chat.type == ChatType.CHANNEL:
                channel_ids.append(dialog.chat.id)
        found = len(channel_ids)
        for idx, channel_id in enumerate(channel_ids, 1):
            try:
                await client.leave_chat(channel_id)
                deleted += 1
                await msg.edit(f"در حال ترک کانال {deleted} از {found} ...")
                await asyncio.sleep(0.2)
            except Exception as e:
                print(f"خطا در ترک کانال {channel_id}: {e}")
        await msg.edit(
            f"✅ پاکسازی کانال‌ها تمام شد!\n"
            f"تعداد کل کانال‌ها: {found}\n"
            f"تعداد موفق ترک شده: {deleted}\n"
            f"{'تمام کانال‌ها ترک شدند.' if deleted==found else 'برخی کانال‌ها ترک نشدند.'}"
        )
        return True
    return False

# ====== ارسال و فوروارد گروهی ======
async def get_my_chats(client, types):
    chats = []
    async for dialog in client.get_dialogs():
        if dialog.chat.type in types:
            chats.append(dialog.chat.id)
    return chats

async def get_contacts(client):
    contacts = []
    users = await client.get_contacts()
    for user in users:
        contacts.append(user.id)
    return contacts

async def send_to_chats(client, message, chat_ids, text=None, forward=False):
    sent = 0
    failed = 0
    for chat_id in chat_ids:
        try:
            if forward and message.reply_to_message:
                await client.forward_messages(chat_id, message.chat.id, message.reply_to_message.id)
            elif text:
                await client.send_message(chat_id, text)
            elif message.reply_to_message:
                await message.reply_to_message.copy(chat_id)
            else:
                continue
            sent += 1
            await asyncio.sleep(0.2)
        except (PeerIdInvalid, UserIsBlocked):
            failed += 1
        except Exception as e:
            print(f"[send_to_chats] Error for {chat_id}: {e}")
            failed += 1
    return sent, failed

async def animated_waiting(msg, stop_event):
    FRAMES = [
        "⏳ منتظر بمانید...\n[░░░░░░░░░░]",
        "⏳ منتظر بمانید...\n[█░░░░░░░░░]",
        "⏳ منتظر بمانید...\n[██░░░░░░░░]",
        "⏳ منتظر بمانید...\n[███░░░░░░░]",
        "⏳ منتظر بمانید...\n[████░░░░░░]",
        "⏳ منتظر بمانید...\n[█████░░░░░]",
        "⏳ منتظر بمانید...\n[██████░░░░]",
        "⏳ منتظر بمانید...\n[███████░░░]",
        "⏳ منتظر بمانید...\n[████████░░]",
        "⏳ منتظر بمانید...\n[█████████░]",
        "⏳ منتظر بمانید...\n[██████████]",
    ]
    last = None
    i = 0
    while not stop_event.is_set():
        frame = FRAMES[i % len(FRAMES)]
        if frame != last:
            try:
                await msg.edit(frame)
            except Exception as e:
                if "MESSAGE_NOT_MODIFIED" not in str(e):
                    print(f"[animated_waiting] {e}")
            last = frame
        i += 1
        await asyncio.sleep(0.2)

async def handle_send_commands(client, m):
    text = m.text or ""
    cmd = text.strip().lower()

    commands = {
        "ارسال به پیوی": {"types": [ChatType.PRIVATE], "forward": False},
        "send to privates": {"types": [ChatType.PRIVATE], "forward": False},
        "ارسال به گروه": {"types": [ChatType.GROUP, ChatType.SUPERGROUP], "forward": False},
        "send to groups": {"types": [ChatType.GROUP, ChatType.SUPERGROUP], "forward": False},
        "ارسال به همه": {"types": [ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP], "forward": False},
        "send to all": {"types": [ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP], "forward": False},
        "ارسال به مخاطبین": {"types": [], "contacts": True, "forward": False},
        "send to contacts": {"types": [], "contacts": True, "forward": False},
        "فوروارد به پیوی": {"types": [ChatType.PRIVATE], "forward": True},
        "forward to privates": {"types": [ChatType.PRIVATE], "forward": True},
        "فوروارد به گروه": {"types": [ChatType.GROUP, ChatType.SUPERGROUP], "forward": True},
        "forward to groups": {"types": [ChatType.GROUP, ChatType.SUPERGROUP], "forward": True},
        "فوروارد به همه": {"types": [ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP], "forward": True},
        "forward to all": {"types": [ChatType.PRIVATE, ChatType.GROUP, ChatType.SUPERGROUP], "forward": True},
        "فوروارد به مخاطبین": {"types": [], "contacts": True, "forward": True},
        "forward to contacts": {"types": [], "contacts": True, "forward": True},
    }

    found = None
    for key in commands:
        if cmd.startswith(key):
            found = key
            break
    if not found:
        return False

    params = commands[found]

    # استخراج متن اضافه دقیق
    extra_text = None
    remain = text[len(found):].strip()
    if remain:
        extra_text = remain

    if not m.reply_to_message and not extra_text:
        await m.reply("لطفاً روی یک پیام ریپلای کنید یا متنی بعد از دستور بنویسید.")
        return True

    if params.get("contacts"):
        chat_ids = await get_contacts(client)
    else:
        chat_ids = await get_my_chats(client, params["types"])

    if not chat_ids:
        await m.reply("هیچ چتی پیدا نشد.")
        return True

    waiting = await m.reply("⏳ منتظر بمانید...\n[░░░░░░░░░░]")
    stop_event = asyncio.Event()
    task = asyncio.create_task(animated_waiting(waiting, stop_event))

    sent, failed = await send_to_chats(
        client=client,
        message=m,
        chat_ids=chat_ids,
        text=extra_text,
        forward=params["forward"]
    )

    stop_event.set()
    await task

    await waiting.edit(f"✅ ارسال/فوروارد انجام شد!\nموفق: {sent}\nناموفق: {failed}")
    return True

# ====== بلاک کردن کاربر ======
async def handle_block(message):
    """
    هندلر مسدودسازی کاربر با دستور "مسدود" یا "بلاک"
    استفاده در کد اصلی: if await handle_block(m): return
    """
    command = message.text.strip().lower()
    if command not in ["مسدود", "بلاک"]:
        return False

    target_id = None
    target_info = None

    # حالت ریپلای به پیام کاربر دیگر
    if message.reply_to_message and message.reply_to_message.from_user:
        user = message.reply_to_message.from_user
        target_id = user.id
        name = ((user.first_name or "") + (" " + user.last_name if getattr(user, "last_name", None) else "")).strip()
        username = f"@{user.username}" if getattr(user, 'username', None) else ""
        target_info = f"{username} ({name})" if username else name
    # حالت پیوی (نه Saved Messages)
    elif message.chat.type == "private":
        my_id = (await message._client.get_me()).id
        # فقط اگر با خودت چت نمی‌کنی (Saved Messages نباشد)
        if message.chat.id != my_id:
            target_id = message.chat.id
            user = await message._client.get_users(target_id)
            name = ((user.first_name or "") + (" " + user.last_name if getattr(user, "last_name", None) else "")).strip()
            username = f"@{user.username}" if getattr(user, 'username', None) else ""
            target_info = f"{username} ({name})" if username else name

    if not target_id:
        await message.edit_text("❗ لطفاً روی پیام کاربر ریپلای کن یا در پیوی کاربر باش.")
        return True

    try:
        await message._client.block_user(target_id)
        if not target_info:
            target_info = str(target_id)
        await message.edit_text(f"⛔ کاربر {target_info} با موفقیت مسدود شد.")
    except Exception as e:
        await message.edit_text(f"خطا در مسدودسازی کاربر:\n{e}")
    return True

# ====== نمایش لیست کاربران بلاک شده ======
async def get_blocked_users(client):
    blocked = []
    offset = 0
    limit = 100
    while True:
        result = await client.invoke(
            functions.contacts.GetBlocked(offset=offset, limit=limit)
        )
        users = result.users
        if not users:
            break
        blocked.extend(users)
        if len(users) < limit:
            break
        offset += len(users)
    return blocked

def format_blocked_users(users):
    if not users:
        return (
            "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "🚫 هیچ کاربر بلاک‌شده‌ای وجود ندارد.\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━┛"
        )
    lines = ["┏━━ 📛 لیست کاربران بلاک‌شده ━━┓"]
    for i, user in enumerate(users, 1):
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username = f"@{user.username}" if user.username else ""
        display = f"{username} ({name})" if username else name
        lines.append(f"{i}. {display}")
    lines.append("┗━━━━━━━━━━━━━━━━━━━━━━┛")
    return "\n".join(lines)

async def handle_blocked(message):
    """
    استفاده به شکل if await handle_blocked(m): return
    """
    if message.text.strip().lower() in ["لیست بلاک", "blocked list"]:
        users = await get_blocked_users(message._client)
        text = format_blocked_users(users)
        await message.edit_text(text)
        return True
    return False

# --------- هواشناسی و تاریخ زیبای شمسی ---------
WEATHER_API_URL = "https://api.codesazan.ir/Weather/"
WEATHER_API_KEY = "5994044255:bBY3e25heh@CodeSazan_APIManager_Bot"

async def get_weather(city):
    try:
        url = (
            f"{WEATHER_API_URL}"
            f"?key={WEATHER_API_KEY}"
            f"&type=Weather&city={city}"
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and data.get("status") == 200 and data.get("result"):
                        return data["result"]
    except Exception as e:
        print(f"weather error: {e}")
    return None

def format_weather(result):
    return (
        f"🌤️ <b>وضعیت آب‌وهوا برای:</b> <code>{result.get('address', '')}</code>\n"
        f"کشور: {result.get('flag','')} {result.get('country','')} | استان: {result.get('state','')} | شهر: {result.get('city','')}\n"
        f"مختصات: {result.get('latitude','')} ، {result.get('longitude','')}\n"
        f"تاریخ: {result.get('date','')} | ساعت: {result.get('time','')}\n"
        f"وضعیت: <b>{result.get('weather_conditions','')}</b>\n"
        f"🌡️ دما: <b>{result.get('degree','')}</b>\n"
        f"💧 رطوبت: {result.get('humidity','')} | فشار: {result.get('pressure','')}\n"
        f"💨 سرعت باد: {result.get('speed','')}\n"
        f"🌅 طلوع: {result.get('sunrise',{}).get('time','')}\n"
        f"🌇 غروب: {result.get('sunset',{}).get('time','')}\n"
        f"📍 منطقه زمانی: {result.get('time_zone','')}"
    )
def get_beautiful_date():
    import jdatetime
    from pytz import timezone
    from datetime import datetime
    tehran = timezone("Asia/Tehran")
    now = datetime.now(tehran)
    persian = jdatetime.datetime.fromgregorian(datetime=now)
    weekday_map = {
        "Saturday": "شنبه", "Sunday": "یکشنبه", "Monday": "دوشنبه",
        "Tuesday": "سه‌شنبه", "Wednesday": "چهارشنبه",
        "Thursday": "پنجشنبه", "Friday": "جمعه"
    }
    weekday = weekday_map[now.strftime("%A")]
    month_map = {
        1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر", 5: "مرداد",
        6: "شهریور", 7: "مهر", 8: "آبان", 9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
    }
    jalali_str = f"{weekday} {persian.day} {month_map[persian.month]} {persian.year}"
    gregorian_str = now.strftime("%d %B %Y")
    return f"📆 {jalali_str} - {gregorian_str}"

async def handle_weather_and_date(message):
    text = (message.text or "").strip()
    # تاریخ
    if text in ["تاریخ", "date"]:
        await message.edit_text(get_beautiful_date())
        return True
    # هواشناسی/هوا
    if text.startswith("هوا ") or text.startswith("هواشناسی "):
        city = text.split(" ", 1)[1].strip() if " " in text else ""
        if not city:
            await message.edit_text("❗ لطفا نام شهر را بعد از 'هوا' بنویسید.\nمثال: هوا تهران")
            return True
        msg = await message.edit_text(f"⏳ دریافت اطلاعات آب‌وهوا برای {city} ...")
        result = await get_weather(city)
        if result and result.get("city"):
            text = format_weather(result)
            await msg.edit(text)
        else:
            await msg.edit(f"❌ اطلاعات آب‌وهوا برای '{city}' یافت نشد.")
        return True
    return False
# ========== هندلر اصلی ==========
@app.on_message(filters.text & filters.me)
async def handle(_, m: Message):
    text = m.text
    if await handle_weather_and_date(m): return
    if await handle_privet(m): return
    if await handle_blocked(m): return
    if await handle_block(m): return
    if await handle_send_commands(app, m): return
    if await handle_joke(m): return
    if await handle_bio(m): return
    if text and text.strip().startswith("طلا"):
        if await handle_tala_command(m): return
    if await handle_tag_admin(app, m): return

    if text in {".help", "/help"}:
        mention = (await app.get_me()).mention
        await m.edit_text(HELP_TEXT.format(mention=mention))
    elif text in {".ping", "/ping"}:
        try:
            ping = psutil.getloadavg()
            process = psutil.Process(os.getpid())
            ram = size(process.memory_info().rss)
            await m.edit(f"❅ **Ping**: `{ping[0]}`\n❅ Ram:`{ram}`")
        except Exception as e:
            await m.edit(f"Error in ping: {e}")
    elif text.startswith(".gpt"):
        await handle_gpt(m)
        return

    settings = {
        ".timename ": "timename",
        ".timebio ": "timebio",
        ".online ": "online",
        ".playing ": "playing",
        ".typing ": "typing"
    }
    for prefix, setting_key in settings.items():
        if text.startswith(prefix):
            replace = text.replace(prefix, "")
            if replace in ["on", "off"]:
                try:
                    data[setting_key] = replace
                    write_json("Setting.json", data)
                    await m.edit(f"**• {setting_key.replace('_', ' ').capitalize()} is {replace}**")
                except Exception as e:
                    await m.edit(f"Error in {setting_key}: {e}")
            break
    else:
        if text == ".status":
            pl = ""
            md = data.items()
            lines = [f"❖ {key} -> {value}" for key, value in md]
            pl = "\n".join(lines)
            await m.edit_text(f"{pl}")
        elif await handle_delete_GROP(app, m):
            return
        elif await handle_delete_CHANEL(app, m):
            return

# ========== زمان‌بندی ==========
scheduler = AsyncIOScheduler()
scheduler.add_job(update_profile, "interval", seconds=10)
scheduler.add_job(online, "interval", seconds=45)
scheduler.start()

if __name__ == "__main__":
    app.start()
    print("Started ...")
    app.send_message("me", "🟢 **Bot is up and running!**")
    idle()
    app.stop()