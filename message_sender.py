from telethon import TelegramClient
import asyncio
import time
from data import phone, id, hash, m_phone

api_id = id
api_hash = hash

my_phone = m_phone
target_phone = phone

repeat_count = 50
delay_seconds = 0.1

message = "😝"

async def main():
    client = TelegramClient("session", api_id, api_hash)
    await client.start(my_phone)

    print("Начал отправку")

    for i in range(repeat_count):
        await client.send_message(target_phone, message)
        print(f"Сообщение отправлено: {i + 1}")

        time.sleep(delay_seconds)

    await client.disconnect()
    print("Готово")

asyncio.run(main())
