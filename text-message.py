from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
import random
import asyncio
import time
import re
from students import student
from data import phone, id, hash, m_phone

api_id = id
api_hash = hash
my_phone = m_phone

yuborilmaganlar = []  # Список для тех, кому НЕ отправили
yuborilganlar = []    # Список для тех, кому отправили

def normalize_phone(phone):
    if not phone:
        return None
    
    phone = str(phone).strip()
    
    if ' ' in phone and len(phone.split()) > 1:
        parts = phone.split()
        for part in parts:
            part = re.sub(r'\D', '', part)
            if len(part) >= 9:
                phone = part
                break
        else:
            phone = re.sub(r'\D', '', parts[0])
    else:
        phone = re.sub(r'\D', '', phone)
    
    # Добавляем код страны если нужно
    if phone.startswith('998'):
        return phone
    elif phone.startswith('8') and len(phone) == 11:
        phone = '7' + phone[1:]
        return phone
    elif len(phone) == 9:
        return '998' + phone
    elif len(phone) == 10 and phone.startswith('9'):
        return '7' + phone
    elif len(phone) >= 10:
        return phone
    
    return None

async def main():
    client = TelegramClient("session", api_id, api_hash)
    await client.start(my_phone)

    print("🔍 Начинаю обработку номеров...")
    
    valid_students = []
    invalid_students = []
    
    for name, phone in student.items():
        normalized_phone = normalize_phone(phone)
        if normalized_phone:
            valid_students.append((name, normalized_phone))
        else:
            invalid_students.append((name, phone))
            yuborilmaganlar.append(f"{name}: {phone} (невалидный номер)")

    print(f"\n📊 Статистика:")
    print(f"   Всего студентов: {len(student)}")
    print(f"   Валидные номера: {len(valid_students)}")
    print(f"   Невалидные номера: {len(invalid_students)}")
    
    if not valid_students:
        print("\n❌ Нет валидных номеров для отправки!")
        await client.disconnect()
        return

    random.shuffle(valid_students)
    print("🔄 Список перемешан для случайного порядка отправки")
    
    daily_limit = 50
    sent_count = 0
    
    print(f"\n{'='*50}")
    print(f"🚀 НАЧИНАЮ ПОСЛЕДОВАТЕЛЬНУЮ ОТПРАВКУ")
    print(f"📊 Лимит на сегодня: {daily_limit} сообщений")
    print(f"{'='*50}\n")
    
    for idx, (student_name, phone_number) in enumerate(valid_students, 1):
        if sent_count >= daily_limit:
            print(f"\n⚠️ Достигнут дневной лимит ({daily_limit} сообщений)")
            break
        
        print(f"\n📋 Контакт {idx}/{len(valid_students)}: {student_name}")
        
        try:
            contact = InputPhoneContact(
                client_id=random.randint(0, 1000000),
                phone=phone_number,
                first_name=student_name[:25],
                last_name=""
            )
            
            result = await client(ImportContactsRequest([contact]))
            
            if not result.users:
                print(f"❌ Не удалось импортировать контакт: {student_name}")
                yuborilmaganlar.append(f"{student_name}: {phone_number} (не импортирован)")
                continue
                
            user = result.users[0]
            print(f"✅ Контакт импортирован: {user.phone}")
            
            message = (
                'Message text goes here...'
            )
            
            await client.send_message(user.id, message)
            sent_count += 1
            print(f"✅ {sent_count}. Сообщение отправлено: {student_name}")
            yuborilganlar.append(f"{student_name}: {phone_number}")
            
            if idx < len(valid_students) and sent_count < daily_limit:
                delay = random.uniform(30, 90)  # 30-90 секунд
                print(f"⏱️ Пауза: {delay:.1f} секунд")
                time.sleep(delay)
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Ошибка при обработке {student_name}: {error_msg}")
            
            if "Too many" in error_msg:
                reason = "слишком много запросов"
                error_delay = random.uniform(30, 60)
                print(f"⚠️ Длительная пауза после ограничения: {error_delay:.1f} сек")
                time.sleep(error_delay)
            else:
                reason = "ошибка отправки"
                error_delay = random.uniform(60, 90)
                print(f"⚠️ Пауза после ошибки: {error_delay:.1f} сек")
                time.sleep(error_delay)
            
            yuborilmaganlar.append(f"{student_name}: {phone_number} ({reason})")
            
            continue
        
        if sent_count % 15 == 0 and sent_count > 0 and sent_count < daily_limit:
            long_break = random.uniform(30, 60)
            print(f"\n⏸️ ДЛИННЫЙ ПЕРЕРЫВ на {long_break/60:.1f} минут")
            time.sleep(long_break)

    await client.disconnect()
    
    print("\n" + "="*60)
    print("📊 ФИНАЛЬНЫЙ ОТЧЕТ:")
    print("="*60)
    
    invalid_count = len([x for x in yuborilmaganlar if "невалидный номер" in x])
    error_count = len([x for x in yuborilmaganlar if "невалидный номер" not in x])
    
    print(f"\n✅ УСПЕШНО отправлено: {len(yuborilganlar)}")
    print(f"❌ НЕ отправлено: {len(yuborilmaganlar)}")
    print(f"   ├─ Невалидные номера: {invalid_count}")
    print(f"   └─ Ошибки отправки: {error_count}")
    
    if yuborilganlar:
        with open("sent_successfully.txt", "w", encoding="utf-8") as f:
            f.write("📋 СПИСОК УСПЕШНО ОТПРАВЛЕННЫХ СООБЩЕНИЙ\n")
            f.write("="*60 + "\n\n")
            for i, item in enumerate(yuborilganlar, 1):
                f.write(f"{i}. {item}\n")
        print(f"\n📄 Список отправленных сохранен в: sent_successfully.txt")
    
    if yuborilmaganlar:
        print("\n" + "="*60)
        print("❌ СПИСОК ТЕХ, КОМУ НЕ БЫЛ ОТПРАВЛЕН СМС:")
        print("="*60)
        
        invalid_numbers = [x for x in yuborilmaganlar if "невалидный номер" in x]
        failed_sending = [x for x in yuborilmaganlar if "невалидный номер" not in x]
        
        if invalid_numbers:
            print("\n📵 НЕВАЛИДНЫЕ НОМЕРА (нельзя отправить):")
            for item in invalid_numbers:
                print(f"  • {item}")
        
        if failed_sending:
            print("\n⚠️ НЕОТПРАВЛЕННЫЕ ИЗ-ЗА ОШИБОК (можно попробовать позже):")
            for item in failed_sending:
                print(f"  • {item}")
        
        # Сохраняем в файл
        with open("not_sent.txt", "w", encoding="utf-8") as f:
            f.write("📋 СПИСОК ТЕХ, КОМУ НЕ БЫЛО ОТПРАВЛЕНО СООБЩЕНИЕ\n")
            f.write("="*60 + "\n\n")
            
            if invalid_numbers:
                f.write("НЕВАЛИДНЫЕ НОМЕРА:\n")
                f.write("-"*40 + "\n")
                for item in invalid_numbers:
                    f.write(f"• {item}\n")
                f.write("\n")
            
            if failed_sending:
                f.write("ОШИБКИ ОТПРАВКИ:\n")
                f.write("-"*40 + "\n")
                for item in failed_sending:
                    f.write(f"• {item}\n")
        
        print(f"\n📄 Полный список неотправленных сохранен в: not_sent.txt")
    
    if yuborilganlar or yuborilmaganlar:
        total_processed = len(yuborilganlar) + len([x for x in yuborilmaganlar if "невалидный номер" not in x])
        if total_processed > 0:
            success_rate = (len(yuborilganlar) / total_processed * 100)
            print(f"\n📈 Успешность отправки: {success_rate:.1f}%")

asyncio.run(main())