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

class MyPayload2(CallbackPayload, prefix='mypayload2'):
   foo: str
   action: str

class MyPayload3(CallbackPayload, prefix='mypayload3'):
   foo: str
   action: str

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
            payload=MyPayload1(foo='create_task', action='edit').pack(),
        )
    )
    builder.row(
        CallbackButton(
            text='Управление категориями',
            payload=MyPayload2(foo='manage_category', action='edit').pack(),
        )
    )
    builder.row(
        CallbackButton(
            text='Посмотреть ближайшие задачи',
            payload=MyPayload3(foo='nearest_task', action='edit').pack(),
        )
    )

    await event.message.answer(
        text = 'Вот мои команды:',
        attachments = [
            builder.as_markup(),
        ]
    )

categories = ['Cat1', 'Cat2', 'Cat3'] #информация о категория должны приходить с бэка

class MyCategoryPayload(CallbackPayload, prefix='category'):
    foo: str
    text: str

@dp.message_callback(MyPayload1.filter(F.foo == 'create_task'))
async def create_task(event: MessageCallback, payload: MyPayload1):
    categoryButton = InlineKeyboardBuilder()

    for idx, category in enumerate(categories):
        payload_packed = MyCategoryPayload(foo=str(idx), text=category).pack()

        categoryButton.row(
            CallbackButton(
                text=category,
                payload=payload_packed
            )
        )
    await event.message.answer(
        text = 'Выберете категорию задачи',
        attachments = [
            categoryButton.as_markup(),
        ]
    )

    @dp.message_callback(MyCategoryPayload.filter())
    async def switch_category(event: MessageCallback, payload: MyCategoryPayload):
        await event.message.answer(
            text='Категория ' + payload.text + ' выбрана. Введите описание задачи:',
            attachments=[]
        )

        # надо еще придумать как выключать прослушивание после получения 1 сообщения
        @dp.message_created(F.message.body.text)
        async def echo_task(event: MessageCreated):
            # msg передается к ии для дальнейшей обработки
            msg = event.message.body.text
            await event.message.answer(F'Ваша новая задача: {msg}') #Вместо msg должна выводиться задача сгенерированная на бэке

class MyPayload4(CallbackPayload, prefix='mypayload4'):
   foo: str
   action: str

@dp.message_callback(MyPayload2.filter(F.foo == 'manage_category'))
async def manage_category(event: MessageCallback, payload: MyPayload2):
    categoryButton = InlineKeyboardBuilder()

    categoryButton.row(
        CallbackButton(
            text='Создать категорию',
            payload=MyPayload4(foo='create_category', action='edit').pack(),
        )
    )

    for idx, category in enumerate(categories):
        payload_packed = MyCategoryPayload(foo=str(idx), text=category).pack()

        categoryButton.row(
            CallbackButton(
                text=category,
                payload=payload_packed
            )
        )

    await event.message.answer(
        text = 'Ваши категории:',
        attachments = [
            categoryButton.as_markup()
        ]
    )

    @dp.message_callback(MyPayload4.filter(F.foo == 'create_category'))
    async def create_category(event: MessageCallback, payload: MyPayload4):
        await event.message.answer(
            text='Введите название категории:',
            attachments=[]
        )

        @dp.message_created(F.message.body.text)
        async def echo(event: MessageCreated):
            # cat передается к ии для создания новой категории в бд
            cat = event.message.body.text
            await event.message.answer(F'Ваша новая категория: {cat}')

    @dp.message_callback(MyCategoryPayload.filter())
    async def switch_category(event: MessageCallback, payload: MyCategoryPayload):
        await event.message.answer(
            text='Категория ' + payload.text + ' выбрана. Что изменить?',
            attachments=[]
        )

tasks = ['Task1', 'Task2', 'Task3'] #информация о ближайших задачах должны приходить с бэка

class MyTaskPayload(CallbackPayload, prefix='category'):
    foo: str
    text: str

@dp.message_callback(MyPayload3.filter(F.foo == 'nearest_task'))
async def nearest_task(event: MessageCallback, payload: MyPayload3):
    nearestTaskButton = InlineKeyboardBuilder()

    for idx, task in enumerate(tasks):
        payload_packed = MyCategoryPayload(foo=str(idx), text=task).pack()

        nearestTaskButton.row(
            CallbackButton(
                text=task,
                payload=payload_packed
            )
        )

    await event.message.answer(
        text = 'Ваши ближайшие задачи:',
        attachments = [
            nearestTaskButton.as_markup()
        ]
    )

    @dp.message_callback(MyTaskPayload.filter())
    async def switch_task(event: MessageCallback, payload: MyTaskPayload):
        await event.message.answer(
            text='Задача ' + payload.text + ' выбрана. Вот ее содержание:',
            attachments=[]
        )
        await event.message.answer(
            text='Абоба', #тут должен выводится содержание задачи с бэка
            attachments=[]
        )

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())