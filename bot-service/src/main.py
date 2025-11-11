import asyncio
import logging
from argparse import Action
from typing import Any, Dict, Optional

from maxapi import Bot, Dispatcher, F
from maxapi.filters import BaseFilter
from maxapi.filters.callback_payload import CallbackPayload
from maxapi.types import (
    BotStarted,
    CallbackButton,
    Command,
    MessageCallback,
    MessageCreated,
    UpdateUnion,
)
from maxapi.types.callback import Callback
from maxapi.types.chats import Chat
from maxapi.types.message import Message
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from settings import settings

bot = Bot(settings.BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


"""
NOTE ПРОЧИТАТЬ ОЛЕГ ЧИТАЙ

Дабы не городить вложенных функций якобы для того чтобы хендлер не вызывался несколько раз,
умные умы разработчиков aiogram и прочих либ для разработки ботов придумали такую вещь как стейты.
Стейты реализуются на фильтрах, ставится стейт на запросе нужных данных, после запроса этих данных стейт убирается и хандлер уже не работает.
Фильтры в библиотеке maxapi реализованы поэтому проблем нет

Использование

# В хандлере указывается фильтр State
@dp.message_created(StateFilter(WAITING_CREATE_CATEGORY))
... code ...

Для указания стейта используется

# Для получения стейта этого чата стейт + данные которые можно сохранить в данном контексте (любые)
chat_id = str(event.get_ids()[0])
state = FSMContext(chat_id)
data = await state.get_data()

# указание стейта (стейты пока-что константы но будут переделаны для добавления можешь новые константы объявлять)
await state.set_state(WAITING_DESCRIPTION)

# добавление данных в контекст
await state.update_data({"selected_category": payload.text})

# получение данных из контекста
category = data.get("selected_category", "Unknown")

"""
user_states: Dict[str, str] = {}
user_data: Dict[str, Dict[str, Any]] = {}  # Для хранения контекста, как state.data


async def get_state(chat_id: str) -> Optional[str]:
    return user_states.get(chat_id)


async def set_state(chat_id: str, state: str):
    user_states[chat_id] = state


async def clear_state(chat_id: str):
    user_states.pop(chat_id, None)
    user_data.pop(chat_id, None)


class FSMContext:
    def __init__(self, chat_id: str):
        self.chat_id = chat_id

    async def get_state(self) -> Optional[str]:
        return await get_state(self.chat_id)

    async def set_state(self, state: str):
        await set_state(self.chat_id, state)

    async def clear(self):
        await clear_state(self.chat_id)

    # Data methods (как в aiogram)
    async def get_data(self) -> Dict[str, Any]:
        return user_data.get(self.chat_id, {})

    async def update_data(self, data: Dict[str, Any]):
        current = await self.get_data()
        current.update(data)
        user_data[self.chat_id] = current

    async def set_data(self, data: Dict[str, Any]):
        user_data[self.chat_id] = data


class StateFilter(BaseFilter):
    def __init__(self, *states: str | None):
        if not states:
            raise ValueError("At least one state is required")
        self.states = states

    async def __call__(self, event: UpdateUnion) -> bool:
        print(self.states)
        if isinstance(event, MessageCreated | MessageCallback):
            if not isinstance(event.chat, Chat):
                return False
            chat_id = str(event.chat.chat_id)
            current_state = await get_state(chat_id)
            for state in self.states:
                if state == "*" or state is None:
                    return True
                if current_state == state:
                    return True
            return False
        else:
            return False


# Стейты пока константами так (переделаю по нормальному)
# FIXME
WAITING_DESCRIPTION = "waiting_description"
WAITING_CREATE_CATEGORY = "waiting_create_name"
WAITING_EDIT_CATEGORY = "waiting_edit_category"


class ActionButton(CallbackPayload, prefix="action"):
    foo: str
    action: str


class TextButton(CallbackPayload, prefix="text"):
    foo: str
    text: str


@dp.bot_started()
async def bot_started(event: BotStarted):
    await bot.send_message(
        chat_id=event.chat_id,
        text="Привет! Я бот для повышения твоей эффективности.\n\n"
        "Со мной ты можешь:\n"
        "1) Создавать для себя задачи\n"
        "2) Делить задачи по категориям\n"
        "3) Ставить задачи перед своей командой, добавляя новых пользователей\n\n"
        "А главное - я сформирую задачи за тебя! С тебя требуется только ввести описание задачи, остальное будет на мне!\n\n"
        "Теперь пропиши команду /start, что бы начать использование бота.",
    )


@dp.message_created(Command("start"))
async def start(event: MessageCreated):
    builder = InlineKeyboardBuilder()

    # Уходит запрос на бэкэнд

    builder.row(
        CallbackButton(
            text="Создать задачу",
            payload=ActionButton(foo="create_task", action="edit").pack(),
        )
    )
    builder.row(
        CallbackButton(
            text="Управление категориями",
            payload=ActionButton(foo="manage_category", action="edit").pack(),
        )
    )
    builder.row(
        CallbackButton(
            text="Посмотреть ближайшие задачи",
            payload=ActionButton(foo="nearest_task", action="edit").pack(),
        )
    )

    await event.message.answer(
        text="Вот мои команды:",
        attachments=[
            builder.as_markup(),
        ],
    )


categories = ["Cat1", "Cat2", "Cat3"]  # информация о категория должны приходить с бэка


@dp.message_callback(ActionButton.filter(F.foo == "create_task"))
async def create_task(event: MessageCallback, payload: ActionButton):
    # Интересная реализация в либе?
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    await state.update_data({"context": "create_task"})

    categoryButton = InlineKeyboardBuilder()

    for idx, category in enumerate(categories):
        payload_packed = TextButton(foo=str(idx), text=category).pack()
        categoryButton.row(CallbackButton(text=category, payload=payload_packed))

    await event.message.answer(
        text="Выберете категорию задачи",
        attachments=[
            categoryButton.as_markup(),
        ],
    )


@dp.message_callback(TextButton.filter())
async def process_category_selection(event: MessageCallback, payload: TextButton):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    data = await state.get_data()

    context = data.get("context", "")
    if context == "create_task":
        await state.update_data({"selected_category": payload.text})
        await state.set_state(WAITING_DESCRIPTION)
        await event.message.answer(
            text=f"Категория {payload.text} выбрана. Введите описание задачи:",
            attachments=[],
        )
    elif context == "manage_category":
        # Логика для manage: например, edit
        await state.update_data({"selected_category": payload.text})
        await state.set_state(WAITING_EDIT_CATEGORY)
        await event.message.answer(
            text=f"Категория {payload.text} выбрана. Введите текст",
            attachments=[],
        )
    # Другие контексты...


# Хендлер для текста: только в стейте WAITING_DESCRIPTION
@dp.message_created(StateFilter(WAITING_DESCRIPTION))
async def process_task_description(event: MessageCreated):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    msg = event.message.body.text

    data = await state.get_data()
    category = data.get("selected_category", "Unknown")

    # Передача на бэк/ИИ: msg + category
    await event.message.answer(
        f'Ваша новая задача в категории "{category}": {msg}'
    )  # Сгенерированная с бэка
    await state.clear()  # Выход


@dp.message_callback(ActionButton.filter(F.foo == "manage_category"))
async def manage_category(event: MessageCallback, payload: ActionButton):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    await state.update_data({"context": "manage_category"})  # Флаг

    categoryButton = InlineKeyboardBuilder()
    categoryButton.row(
        CallbackButton(
            text="Создать категорию",
            payload=ActionButton(foo="create_category", action="edit").pack(),
        )
    )
    for idx, category in enumerate(categories):
        payload_packed = TextButton(foo=str(idx), text=category).pack()
        categoryButton.row(CallbackButton(text=category, payload=payload_packed))
    await event.message.answer(
        text="Ваши категории:", attachments=[categoryButton.as_markup()]
    )


@dp.message_callback(ActionButton.filter(F.foo == "create_category"))
async def start_create_category(event: MessageCallback, payload: ActionButton):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    await state.set_state(WAITING_CREATE_CATEGORY)
    await event.message.answer(text="Введите название категории:", attachments=[])


# Хендлер для текста: только в стейте WAITING_CREATE_CATEGORY
@dp.message_created(StateFilter(WAITING_CREATE_CATEGORY))
async def process_category_name(event: MessageCreated):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    cat = event.message.body.text

    # Передача на бэк/ИИ для создания в БД
    await event.message.answer(f'Ваша новая категория "{cat}" создана!')
    await state.clear()


# Для edit категории (пример обработки ввода)
@dp.message_created(StateFilter(WAITING_EDIT_CATEGORY))
async def process_edit_category(event: MessageCreated):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    input_text = event.message.body.text

    data = await state.get_data()
    category = data.get("selected_category", "Unknown")

    await event.message.answer(f"Выбрана категория: {category} изменения {input_text}")

    await state.clear()


tasks = [
    "Task1",
    "Task2",
    "Task3",
]  # информация о ближайших задачах должны приходить с бэка


@dp.message_callback(TextButton.filter(F.foo == "nearest_task"))
async def nearest_task(event: MessageCallback, payload: TextButton):
    nearestTaskButton = InlineKeyboardBuilder()
    for idx, task in enumerate(tasks):
        payload_packed = TextButton(foo=str(idx), text=task).pack()
        nearestTaskButton.row(CallbackButton(text=task, payload=payload_packed))
    await event.message.answer(
        text="Ваши ближайшие задачи:", attachments=[nearestTaskButton.as_markup()]
    )


@dp.message_callback(TextButton.filter())
async def switch_task(event: MessageCallback, payload: TextButton):
    await event.message.answer(
        text=f'Задача "{payload.text}" выбрана. Вот ее содержание:', attachments=[]
    )
    await event.message.answer(
        text="Абоба: детальное описание с бэка.",  # Содержание с бэка
        attachments=[],
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
