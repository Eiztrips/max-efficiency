import asyncio
import logging

from maxapi.filters.callback_payload import CallbackPayload
from maxapi import Bot, Dispatcher, F
from maxapi.types import Command, MessageCreated, CallbackButton, MessageCallback, BotStarted
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from settings import settings

bot = Bot(settings.BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

class MyPayload1(CallbackPayload, prefix='mypayload1'):
    foo: str
    action: str

#lass MyPayload2(CallbackPayload, prefix='mypayload2'):
#   foo: str
#   action: str

#lass MyPayload3(CallbackPayload, prefix='mypayload3'):
#   foo: str
#   action: str

@dp.bot_started()
async def bot_started(event: BotStarted):
    await bot.send_message(
        chat_id=event.chat_id,
        text='Привет! Я бот для повышения твоей эффективности.\n\n'
             'Со мной ты можешь:\n'
             '1) Создавать для себя задачи\n'
             '2) Делить задачи по категориям\n'
             '3) Ставить задачи перед своей командой, добавляя новых пользователей\n\n'
             'А главное - я сформирую задачи за тебя! С тебя требуется только ввести описание задачи, остальное будет на мне!\n\n'
             'Теперь пропиши команду /start, что бы начать использование бота.',
    )

@dp.message_created(Command('start'))
async def start(event: MessageCreated):
    builder = InlineKeyboardBuilder()

    #Уходит запрос на бэкэнд

    builder.row(
        CallbackButton(
            text='Создать задачу',
            payload=MyPayload1(foo='1', action='edit').pack(),
        )
    )
    builder.row(
        CallbackButton(
            text='Управление категориями',
            payload=MyPayload1(foo='2', action='edit').pack(),
        )
    )
    builder.row(
        CallbackButton(
            text='Посмотреть ближайшие задачи',
            payload=MyPayload1(foo='3', action='edit').pack(),
        )
    )

    await event.message.answer(
        text = 'Вот мои команды:',
        attachments = [
            builder.as_markup(),
        ]
    )

@dp.message_callback(MyPayload1.filter(F.foo == '1'))
async def create_task(event: MessageCallback, payload: MyPayload1):
    await event.message.answer(
        text = 'Опишите задачу',
        attachments = []
    )

@dp.message_callback(MyPayload1.filter(F.foo == '2'))
async def open_category(event: MessageCallback, payload: MyPayload1):
    await event.message.answer(
        text = 'Ваши категории:',
        attachments = []
    )

@dp.message_callback(MyPayload1.filter(F.foo == '3'))
async def nearest_task(event: MessageCallback, payload: MyPayload1):
    await event.message.answer(
        text = 'Ваши ближайшие задачи:',
        attachments = []
    )

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())