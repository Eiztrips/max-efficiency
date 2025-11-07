import asyncio
import logging

from maxapi import Bot, Dispatcher
from maxapi.types import Command, MessageCreated, CallbackButton, MessageCallback, BotStarted
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from settings import settings

bot = Bot(settings.BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

@dp.bot_started()
async def bot_started(event: BotStarted):
    await bot.send_message(
        chat_id=event.chat_id,
        text='Привет! Я бот для повышения твоей эффективности.\n\n'
             'Со мной ты можешь:\n'
             '1) Создавать для себя задачи\n'
             '2) Делить задачи по категориям\n'
             '3) Ставить задачи перед своей командой, добавляя новых пользователей\n\n'
             'А главное - я сформирую задачи за тебя! С тебя требуется только ввести описание задачи, остальное будет на мне!',
    )

@dp.message_created(Command('start'))
async def start(event: MessageCreated):
    builder = InlineKeyboardBuilder()

    #Уходит запрос на бэкэнд

    builder.row(
        CallbackButton(
            text='Создать задачу',
            payload='/btn_1'
        )
    )
    builder.row(
        CallbackButton(
            text='Управление категориями',
            payload='/btn_2',
        ),
        CallbackButton(
            text='Посмотреть ближайшие задачи',
            payload='/btn_3',
        ),
        #
        #    OpenAppButton(
        #        text="Приложение",
        #        web_app="username бота",
        #        contact_id="Идентификатор бота"
        #    )
        #
    )

    await event.message.answer(
        text = 'Вот мои команды:',
        attachments = [
            builder.as_markup(),
        ]
    )

@dp.message_callback(Command('btn_1'))
async def btn_1(event: MessageCallback):
    await event.message.answer(
        text = 'Опишите задачу',
        attachments = []
    )

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())