import asyncio
import datetime
import logging
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
from maxapi.types.chats import Chat
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from . import settings
from .services.user import user_service
from .services.category import category_service
from .services.task import task_service

bot = Bot(settings.BOT_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)


"""
NOTE todos:

- Перенести стейт-машинку в отдельный класс
- сделать рефактор кода не хранить все в мейн
- кастомизировать текст

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
WAITING_TASK_DESCRIPTION = "waiting_task_description"
WAITING_CREATE_CATEGORY = "waiting_create_name"
WAITING_EDIT_CATEGORY = "waiting_edit_category"
WAITING_CATEGORY_DESCRIPTION = "waiting_category_description"
WAITING_EDIT_CATEGORY_DESCRIPTION = "waiting_edit_category_description"
WAITING_TASK_TITLE = "waiting_task_title"
WAITING_TASK_DESCRIPTION_EDIT = "waiting_task_description_edit"

class ActionButton(CallbackPayload, prefix="action"):
    foo: str
    action: str

class TextButton(CallbackPayload, prefix="text"):
    foo: str
    text: str

class TagsButton(CallbackPayload, prefix="tags"):
    foo: str
    text: str

class TaskButton(CallbackPayload, prefix="task"):
    foo: str
    text: str

class TaskActionButton(CallbackPayload, prefix="task_action"):
    task_id: int
    action: str

class CategoryActionButton(CallbackPayload, prefix="cat_action"):
    category_id: int
    action: str

# TODO: МУВ паГИНация ТУ КОР СЕРВИС ЛЕЙТЕР
class PaginationButton(CallbackPayload, prefix="pagination"):
    page: int
    action: str

TASKS_PER_PAGE = 5

class HomeButton(CallbackPayload, prefix="home"):
    action: str

def add_home_button(builder: InlineKeyboardBuilder):
    builder.row(
        CallbackButton(
            text="На главную",
            payload=HomeButton(action="return").pack(),
        )
    )
    return builder

builder = InlineKeyboardBuilder()

builder.row(
    CallbackButton(
        text="Задачи",
        payload=ActionButton(foo="my_tasks", action="edit").pack(),
    ),
    CallbackButton(
        text="Категории",
        payload=ActionButton(foo="manage_category", action="edit").pack(),
    )

)
builder.row(
    CallbackButton(
        text="Создать задачу",
        payload=ActionButton(foo="create_task", action="edit").pack(),
    )
)

async def start_message(event):
    chat_id, user_id = event.get_ids()[0], event.get_ids()[1]
    tasks = task_service.fetch_tasks(
        {"max_user_id": user_id, "to_date": datetime.datetime.now() + datetime.timedelta(days=7)})
    if tasks:
        message_task_info = f"У вас запланировано {len(tasks)} задач на ближайшие 7 дней.\n" + "\n".join(
            [f"- {task['title']}" for task in tasks])
    else:
        message_task_info = "У вас нет запланированных задач на ближайшие 7 дней."
    await bot.send_message(
        chat_id=chat_id,
        text=message_task_info,
        attachments=[
            builder.as_markup(),
        ]
    )

@dp.bot_started()
async def bot_started(event: BotStarted):
    if user_service.get_user_by_max_user_id(event.user.user_id) is None:
        user_service.create_user(
            max_user_id=event.user.user_id,
            username=event.user.username,
        )
        await bot.send_message(
            chat_id=event.chat_id,
            text=f"Привет {event.user.first_name}! Я бот для повышения твоей эффективности.\n\n"
                 "Со мной ты можешь:\n"
                 "1) Создавать для себя задачи\n"
                 "2) Делить задачи по категориям\n"
                 "3) Ставить задачи перед своей командой, добавляя новых пользователей\n\n"
                 "А главное - я сформирую задачи за тебя! С тебя требуется только ввести описание задачи, остальное будет на мне!\n\n",
            attachments=[
                builder.as_markup(),
            ]
        )
    else:
        await start_message(event)

@dp.message_created(Command("start"))
async def start(event: MessageCreated):
    chat_id, user_id = event.get_ids()[0], event.get_ids()[1]
    if user_service.get_user_by_max_user_id(user_id) is None:
        await bot.send_message(
            chat_id=event.chat.chat_id,
            text="Вы не зарегистрированы! Пожалуйста, начните чат со мной снова."
        )
        # В идеале await asyncio.sleep(10) + удаление чата, но либу надо форкать
        return
    await start_message(event)

# -------- Возврат на главную --------

@dp.message_callback(HomeButton.filter(F.action == "return"))
async def return_home(event: MessageCallback, payload: HomeButton):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    await state.clear()
    await bot.delete_message(event.message.body.mid)
    await start_message(event)

# -------- Просмотр всех задач --------

@dp.message_callback(ActionButton.filter(F.foo == "my_tasks"))
async def my_tasks(event: MessageCallback, payload: ActionButton):
    chat_id = str(event.get_ids()[0])
    user_id = event.get_ids()[1]
    state = FSMContext(chat_id)

    tasks = task_service.fetch_tasks({"max_user_id": user_id})

    if not tasks:
        no_tasks_builder = InlineKeyboardBuilder()
        add_home_button(no_tasks_builder)
        await event.message.answer(
            text="У вас пока нет задач",
            attachments=[no_tasks_builder.as_markup()]
        )
        await bot.delete_message(event.message.body.mid)
        return

    await state.update_data({"cached_tasks": tasks})

    await show_tasks_page(event, tasks, page=0, delete_old=True)

@dp.message_callback(PaginationButton.filter(F.action == "my_tasks"))
async def my_tasks_pagination(event: MessageCallback, payload: PaginationButton):
    chat_id = str(event.get_ids()[0])
    user_id = event.get_ids()[1]
    state = FSMContext(chat_id)

    data = await state.get_data()
    tasks = data.get("cached_tasks")

    if not tasks:
        tasks = task_service.fetch_tasks({"max_user_id": user_id})
        await state.update_data({"cached_tasks": tasks})

    if not tasks:
        no_tasks_builder = InlineKeyboardBuilder()
        add_home_button(no_tasks_builder)
        await event.message.answer(
            text="У вас пока нет задач",
            attachments=[no_tasks_builder.as_markup()]
        )
        await bot.delete_message(event.message.body.mid)
        return

    await show_tasks_page(event, tasks, page=payload.page, delete_old=True)

@dp.message_callback(PaginationButton.filter(F.action == "my_tasks"))
async def my_tasks_pagination(event: MessageCallback, payload: PaginationButton):
    user_id = event.get_ids()[1]

    tasks = task_service.fetch_tasks(
        {"max_user_id": user_id}
    )

    if not tasks:
        no_tasks_builder = InlineKeyboardBuilder()
        add_home_button(no_tasks_builder)
        await event.message.answer(
            text="У вас пока нет задач",
            attachments=[no_tasks_builder.as_markup()]
        )
        await bot.delete_message(event.message.body.mid)
        return

    await show_tasks_page(event, tasks, page=payload.page, delete_old=True)

async def show_tasks_page(event: MessageCallback, tasks: list, page: int, delete_old: bool = False):
    total_tasks = len(tasks)
    total_pages = (total_tasks + TASKS_PER_PAGE - 1) // TASKS_PER_PAGE

    if page < 0:
        page = 0
    elif page >= total_pages:
        page = total_pages - 1

    start_idx = page * TASKS_PER_PAGE
    end_idx = min(start_idx + TASKS_PER_PAGE, total_tasks)

    tasks_on_page = tasks[start_idx:end_idx]

    TaskButtonBuilder = InlineKeyboardBuilder()

    for task in tasks_on_page:
        payload_packed = TaskButton(foo=str(task["id"]), text=task["title"]).pack()
        TaskButtonBuilder.row(
            CallbackButton(
                text=task["title"],
                payload=payload_packed
            )
        )

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            CallbackButton(
                text="⬅️ Назад",
                payload=PaginationButton(page=page - 1, action="my_tasks").pack()
            )
        )
    if page < total_pages - 1:
        nav_buttons.append(
            CallbackButton(
                text="Вперёд ➡️",
                payload=PaginationButton(page=page + 1, action="my_tasks").pack()
            )
        )

    if nav_buttons:
        TaskButtonBuilder.row(*nav_buttons)

    add_home_button(TaskButtonBuilder)

    page_info = f"Страница {page + 1} из {total_pages}"
    await event.message.answer(
        text=f'Ваши задачи:\n{page_info}',
        attachments=[
            TaskButtonBuilder.as_markup(),
        ]
    )
    if delete_old:
        await bot.delete_message(event.message.body.mid)

# -------- Создание задачи --------

@dp.message_callback(ActionButton.filter(F.foo == "create_task"))
async def create_task(event: MessageCallback, payload: ActionButton):
    chat_id = str(event.get_ids()[0])
    user_id = event.get_ids()[1]
    state = FSMContext(chat_id)
    await state.update_data({"context": "create_task"})

    categoryButton = InlineKeyboardBuilder()

    categories = user_service.fetch_user_categories(user_id)

    if categories == []:
        no_cat_builder = InlineKeyboardBuilder()
        add_home_button(no_cat_builder)
        await event.message.answer(
            text="У вас нет категорий. Пожалуйста, создайте категорию перед созданием задачи.",
            attachments=[no_cat_builder.as_markup()],
        )
        await bot.delete_message(event.message.body.mid)
        return

    for idx, category in enumerate(categories):
        payload_packed = TextButton(foo=str(category["id"]), text=category["name"]).pack()
        categoryButton.row(CallbackButton(text=category["name"], payload=payload_packed))

    add_home_button(categoryButton)

    await event.message.answer(
        text="Выберете категорию задачи ",
        attachments=[
            categoryButton.as_markup(),
        ],
    )
    await bot.delete_message(event.message.body.mid)

@dp.message_created(StateFilter(WAITING_TASK_DESCRIPTION))
async def process_task_description(event: MessageCreated):
    chat_id = str(event.get_ids()[0])
    user_id = event.get_ids()[1]
    state = FSMContext(chat_id)
    msg = event.message.body.text

    data = await state.get_data()
    category_name = data.get("selected_category", "")
    category_id = data.get("selected_category_id", None)

    task_service.create(max_user_id=user_id, prompt=msg, category_id=category_id)

    await event.message.answer(
        f'Задача в категории "{category_name}" создается...\nОписание: {msg}'
    )
    await start_message(event)
    await state.clear()

# -------- Управление задачами --------

@dp.message_callback(TaskActionButton.filter(F.action == "rename"))
async def rename_task(event: MessageCallback, payload: TaskActionButton):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)

    await state.update_data({"selected_task_id": payload.task_id})
    await state.set_state(WAITING_TASK_TITLE)
    rename_builder = InlineKeyboardBuilder()
    add_home_button(rename_builder)
    await event.message.answer(
        text="Введите новое название задачи:",
        attachments=[rename_builder.as_markup()]
    )
    await bot.delete_message(event.message.body.mid)

@dp.message_callback(TaskActionButton.filter(F.action == "edit_desc"))
async def edit_task_description(event: MessageCallback, payload: TaskActionButton):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)

    await state.update_data({"selected_task_id": payload.task_id})
    await state.set_state(WAITING_TASK_DESCRIPTION_EDIT)
    edit_desc_builder = InlineKeyboardBuilder()
    add_home_button(edit_desc_builder)
    await event.message.answer(
        text="Введите новое описание задачи:",
        attachments=[edit_desc_builder.as_markup()]
    )
    await bot.delete_message(event.message.body.mid)

@dp.message_callback(TaskActionButton.filter(F.action == "delete"))
async def delete_task(event: MessageCallback, payload: TaskActionButton):
    task_id = payload.task_id

    task_service.delete(task_id)

    await event.message.answer(
        text="Задача удалена!",
        attachments=[]
    )
    await bot.delete_message(event.message.body.mid)
    await start_message(event)

@dp.message_created(StateFilter(WAITING_TASK_TITLE))
async def process_rename_task(event: MessageCreated):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    input_text = event.message.body.text

    data = await state.get_data()
    task_id = data.get("selected_task_id")

    if task_id:
        task_service.rename(task_id=task_id, new_title=input_text)
        await event.message.answer(
            f'Название задачи обновлено: "{input_text}"'
        )
    else:
        await event.message.answer("Ошибка: задача не найдена")

    await start_message(event)
    await state.clear()

@dp.message_created(StateFilter(WAITING_TASK_DESCRIPTION_EDIT))
async def process_edit_task_description(event: MessageCreated):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    input_text = event.message.body.text

    data = await state.get_data()
    task_id = data.get("selected_task_id")

    if task_id:
        task_service.rename_description(task_id=task_id, new_description=input_text)
        await event.message.answer(
            'Описание задачи обновлено'
        )
    else:
        await event.message.answer("Ошибка: задача не найдена")

    await start_message(event)
    await state.clear()

# -------- Ближайшие задачи --------
# убрал, они будут отображаться при старте бота

# -------- Поиск задач по тегам --------
# TODO: на бекенде сделать сохранение тегов при создании задачи
"""@dp.message_callback(ActionButton.filter(F.foo == "tasks_on_tags"))
async def select_tag(event: MessageCallback, payload: ActionButton):
    user_id = event.get_ids()[1]
    TagsButtonBuilder = InlineKeyboardBuilder()

    tags = user_service.fetch_user_tags(user_id)

    if not tags:
        await event.message.answer(
            text="У вас пока нет тегов",
            attachments=[]
        )
        await bot.delete_message(event.message.body.mid)
        return

    for idx, tag in enumerate(tags):
        payload_packed = TagsButton(foo=str(tag["id"]), text=tag["name"]).pack()
        TagsButtonBuilder.row(
            CallbackButton(
                text=tag["name"],
                payload=payload_packed
            )
        )

    await event.message.answer(
        text='Выберете интересующий тег',
        attachments=[
            TagsButtonBuilder.as_markup(),
        ]
    )
    await bot.delete_message(event.message.body.mid)
"""

# -------- Создание категории --------

@dp.message_callback(ActionButton.filter(F.foo == "create_category"))
async def start_create_category(event: MessageCallback, payload: ActionButton):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    await state.set_state(WAITING_CREATE_CATEGORY)
    create_cat_builder = InlineKeyboardBuilder()
    add_home_button(create_cat_builder)
    await event.message.answer(text="Введите название категории:", attachments=[create_cat_builder.as_markup()])
    await bot.delete_message(event.message.body.mid)

@dp.message_created(StateFilter(WAITING_CREATE_CATEGORY))
async def process_category_name(event: MessageCreated):
    chat_id = str(event.get_ids()[0])
    user_id = event.get_ids()[1]
    state = FSMContext(chat_id)
    cat = event.message.body.text

    await state.update_data({"new_category_name": cat})
    await state.set_state(WAITING_CATEGORY_DESCRIPTION)
    cat_desc_builder = InlineKeyboardBuilder()
    add_home_button(cat_desc_builder)
    await event.message.answer(text="Введите описание категории:", attachments=[cat_desc_builder.as_markup()])

@dp.message_created(StateFilter(WAITING_CATEGORY_DESCRIPTION))
async def process_category_name(event: MessageCreated):
    chat_id = str(event.get_ids()[0])
    user_id = event.get_ids()[1]
    state = FSMContext(chat_id)
    description_cat = event.message.body.text
    cat = (await state.get_data()).get("new_category_name", "")

    category = category_service.create(user_id, cat, description_cat)

    await event.message.answer(f'Ваша новая категория "{cat}" создана!')
    await start_message(event)
    await state.clear()

# -------- Управление категориями --------

@dp.message_callback(TextButton.filter())
async def process_category_selection(event: MessageCallback, payload: TextButton):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    data = await state.get_data()

    context = data.get("context", "")
    if context == "create_task":
        await state.update_data({
            "selected_category": payload.text,
            "selected_category_id": int(payload.foo)
        })
        await state.set_state(WAITING_TASK_DESCRIPTION)
        task_desc_builder = InlineKeyboardBuilder()
        add_home_button(task_desc_builder)
        await event.message.answer(
            text=f"Категория {payload.text} выбрана. Введите описание задачи:",
            attachments=[task_desc_builder.as_markup()],
        )
        await bot.delete_message(event.message.body.mid)
    elif context == "manage_category":
        category_id = int(payload.foo)
        category = category_service.get_by_id(category_id)

        if not category:
            error_builder = InlineKeyboardBuilder()
            add_home_button(error_builder)
            await event.message.answer(
                text="Категория не найдена",
                attachments=[error_builder.as_markup()]
            )
            await bot.delete_message(event.message.body.mid)
            return

        await state.update_data({
            "selected_category": payload.text,
            "selected_category_id": category_id
        })

        manage_builder = InlineKeyboardBuilder()
        manage_builder.row(
            CallbackButton(
                text="Переименовать",
                payload=CategoryActionButton(category_id=category_id, action="rename").pack(),
            )
        )
        manage_builder.row(
            CallbackButton(
                text="Изменить описание",
                payload=CategoryActionButton(category_id=category_id, action="edit_desc").pack(),
            )
        )
        manage_builder.row(
            CallbackButton(
                text="Удалить категорию",
                payload=CategoryActionButton(category_id=category_id, action="delete").pack(),
            )
        )

        add_home_button(manage_builder)

        category_desc = category.get("description", "Описание отсутствует")
        await event.message.answer(
            text=f'Категория: {payload.text}\nОписание: {category_desc}',
            attachments=[manage_builder.as_markup()]
        )
        await bot.delete_message(event.message.body.mid)

@dp.message_callback(ActionButton.filter(F.foo == "manage_category"))
async def manage_category(event: MessageCallback, payload: ActionButton):
    chat_id = str(event.get_ids()[0])
    user_id = event.get_ids()[1]
    state = FSMContext(chat_id)
    await state.update_data({"context": "manage_category"})

    categoryButton = InlineKeyboardBuilder()
    categoryButton.row(
        CallbackButton(
            text="Создать категорию",
            payload=ActionButton(foo="create_category", action="edit").pack(),
        )
    )

    categories = user_service.fetch_user_categories(user_id)

    for idx, category in enumerate(categories):
        payload_packed = TextButton(foo=str(category["id"]), text=category["name"]).pack()
        categoryButton.row(CallbackButton(text=category["name"], payload=payload_packed))

    add_home_button(categoryButton)

    await event.message.answer(
        text="Ваши категории:", attachments=[categoryButton.as_markup()]
    )
    await bot.delete_message(event.message.body.mid)


# -------- Редактирование категории --------

@dp.message_callback(CategoryActionButton.filter(F.action == "rename"))
async def start_rename_category(event: MessageCallback, payload: CategoryActionButton):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    data = await state.get_data()

    await state.update_data({"selected_category_id": payload.category_id})
    await state.set_state(WAITING_EDIT_CATEGORY)
    rename_cat_builder = InlineKeyboardBuilder()
    add_home_button(rename_cat_builder)
    await event.message.answer(
        text="Введите новое название категории:",
        attachments=[rename_cat_builder.as_markup()]
    )
    await bot.delete_message(event.message.body.mid)

@dp.message_callback(CategoryActionButton.filter(F.action == "edit_desc"))
async def start_edit_category_description(event: MessageCallback, payload: CategoryActionButton):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)

    await state.update_data({"selected_category_id": payload.category_id})
    await state.set_state(WAITING_EDIT_CATEGORY_DESCRIPTION)
    edit_cat_desc_builder = InlineKeyboardBuilder()
    add_home_button(edit_cat_desc_builder)
    await event.message.answer(
        text="Введите новое описание категории:",
        attachments=[edit_cat_desc_builder.as_markup()]
    )
    await bot.delete_message(event.message.body.mid)

@dp.message_created(StateFilter(WAITING_EDIT_CATEGORY))
async def process_rename_category(event: MessageCreated):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    input_text = event.message.body.text

    data = await state.get_data()
    category_name = data.get("selected_category", "Unknown")
    category_id = data.get("selected_category_id")

    if category_id:
        category_service.rename(category_id=category_id, new_name=input_text)
        await event.message.answer(
            f'Категория "{category_name}" переименована в "{input_text}"'
        )
    else:
        await event.message.answer("Ошибка: категория не найдена")

    await start_message(event)
    await state.clear()

@dp.message_created(StateFilter(WAITING_EDIT_CATEGORY_DESCRIPTION))
async def process_edit_category_description(event: MessageCreated):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)
    input_text = event.message.body.text

    data = await state.get_data()
    category_name = data.get("selected_category", "Unknown")
    category_id = data.get("selected_category_id")

    if category_id:
        category_service.rename_description(category_id=category_id, new_description=input_text)
        await event.message.answer(
            f'Описание категории "{category_name}" обновлено'
        )
    else:
        await event.message.answer("Ошибка: категория не найдена")

    await start_message(event)
    await state.clear()

@dp.message_callback(CategoryActionButton.filter(F.action == "delete"))
async def delete_category(event: MessageCallback, payload: CategoryActionButton):
    category_id = payload.category_id

    category_service.delete(category_id)

    await event.message.answer(
        text="Категория удалена!",
        attachments=[]
    )
    await bot.delete_message(event.message.body.mid)
    await start_message(event)

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
