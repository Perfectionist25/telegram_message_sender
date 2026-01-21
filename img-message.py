from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from telethon.errors import FloodWaitError
import asyncio
import time
import random

# ====== ДАННЫЕ АККАУНТА ======
api_id = 31480179
api_hash = "6fd11b2e6281a7e232ed33332c52a75e"
phone = "+998937229889"

# ====== СООБЩЕНИЕ ======
message = """Assalomu alaykum!
Bu rasm bilan birga yuborilgan xabar 😊"""

image_path = "1Презентация.jpg"  # путь к изображению

# ====== СПИСОК НОМЕРОВ ======
phones = [
    "+998936850033",
    # "+998902993609",
]

# ====== ОСНОВНАЯ ЛОГИКА ======
async def main():
    client = TelegramClient("session", api_id, api_hash)
    await client.start(phone)

    # Импорт контактов (БЕЗ изменения имён)
    contacts = []
    for i, p in enumerate(phones):
        contacts.append(
            InputPhoneContact(
                client_id=i,
                phone=p,
                first_name=".",
                last_name=""
            )
        )

    result = await client(ImportContactsRequest(contacts))

    for user in result.users:
        try:
            await client.send_file(
                user.id,
                file=image_path,
                caption=message
            )
            print(f"✅ Отправлено: {user.id}")

            # безопасная пауза
            time.sleep(random.uniform(15, 25))

        except FloodWaitError as e:
            print(f"⏳ FloodWait: ждем {e.seconds} секунд")
            time.sleep(e.seconds)

        except Exception as e:
            print("❌ Ошибка:", e)

    await client.disconnect()

asyncio.run(main())
