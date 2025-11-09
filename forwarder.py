# forwarder.py — пересылка сообщений только из каналов в твой канал

from telethon import TelegramClient, events
import os
import asyncio
from dotenv import load_dotenv

# Загружаем API_ID и API_HASH из .env
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "forwarder_session")

# Твой канал (куда пересылать)
TARGET_CHAT = -1003267261769  # <-- твой ID

# Файл для хранения состояния (ID последних сообщений)
STATE_FILE = "forwarder_state.txt"


# Загружаем состояние
def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    out = {}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                src, mid = line.strip().split(";", 1)
                out[src] = int(mid)
            except:
                pass
    return out


# Сохраняем состояние
def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        for src, mid in state.items():
            f.write(f"{src};{mid}\n")


# Основная логика
async def main():
    state = load_state()
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    @client.on(events.NewMessage)
    async def handler(event):
        # Фильтруем: пересылаем ТОЛЬКО из каналов
        if not event.is_channel:
            return

        chat = await event.get_chat()
        source_id = event.chat_id
        msg_id = event.message.id

        # Проверка — не дублируем одно и то же сообщение
        if state.get(str(source_id)) == msg_id:
            return

        try:
            await client.forward_messages(TARGET_CHAT, event.message)
            print(f"✅ Переслано из: {chat.title} ({source_id})")
            state[str(source_id)] = msg_id
            save_state(state)
        except Exception as e:
            print(f"⚠️ Ошибка при пересылке из {chat.title}: {e}")

    # Запуск клиента
    async with client:
        print("🚀 Forwarder запущен. Ожидание новых сообщений...")
        await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())