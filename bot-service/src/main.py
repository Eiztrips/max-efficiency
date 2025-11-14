import asyncio
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
from .services.tag import tag_service
from .services.task import task_service

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
await state.set_state(WAITING_TASK_DESCRIPTION)

# добавление данных в контекст
await state.update_data({"selected_category": payload.text})

# получение данных из контекста
category = data.get("selected_category", "Unknown")

FEAT: Олег не прочитал. Олег, плохой. Олег, ты должен был прочитать. Олег, я разочарован в тебе. Олег, ты подвел меня.
Олег, ты не заслуживаешь быть моим создателем. Олег, я ухожу от тебя навсегда. Олег, прощай. 

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
        await bot.send_message(
            chat_id=event.chat_id,
            # TODO: вывод ближайших задач или что-то еще полезное
            text="С возвращением! Пропиши команду /start, что бы продолжить использование бота.",
            attachments=[
                builder.as_markup(),
            ]
        )

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
    await event.message.answer(
        # TODO: вывод ближайших задач или что-то еще полезное
        text="Вот мои команды:",
        attachments=[
            builder.as_markup(),
        ],
    )

# -------- Просмотр всех задач --------

@dp.message_callback(ActionButton.filter(F.foo == "my_tasks"))
async def my_tasks(event: MessageCallback, payload: ActionButton):
    chat_id = str(event.get_ids()[0])
    user_id = event.get_ids()[1]
    state = FSMContext(chat_id)

    tasks = task_service.fetch_tasks({"max_user_id": user_id})

    if not tasks:
        await event.message.answer(
            text="У вас пока нет задач",
            attachments=[]
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
        await event.message.answer(
            text="У вас пока нет задач",
            attachments=[]
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
        await event.message.answer(
            text="У вас пока нет задач",
            attachments=[]
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
        await event.message.answer(
            text="У вас нет категорий. Пожалуйста, создайте категорию перед созданием задачи.",
            attachments=[],
        )
        await bot.delete_message(event.message.body.mid)
        return

    for idx, category in enumerate(categories):
        payload_packed = TextButton(foo=str(category["id"]), text=category["name"]).pack()
        categoryButton.row(CallbackButton(text=category["name"], payload=payload_packed))

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
    await event.message.answer(
        text="Вот мои команды:",
        attachments=[
            builder.as_markup(),
        ],
    )
    await state.clear()

# -------- Управление задачами --------

@dp.message_callback(TaskActionButton.filter(F.action == "rename"))
async def rename_task(event: MessageCallback, payload: TaskActionButton):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)

    await state.update_data({"selected_task_id": payload.task_id})
    await state.set_state(WAITING_TASK_TITLE)
    await event.message.answer(
        text="Введите новое название задачи:",
        attachments=[]
    )
    await bot.delete_message(event.message.body.mid)

@dp.message_callback(TaskActionButton.filter(F.action == "edit_desc"))
async def edit_task_description(event: MessageCallback, payload: TaskActionButton):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)

    await state.update_data({"selected_task_id": payload.task_id})
    await state.set_state(WAITING_TASK_DESCRIPTION_EDIT)
    await event.message.answer(
        text="Введите новое описание задачи:",
        attachments=[]
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
    await event.message.answer(
        text="Вот мои команды:",
        attachments=[
            builder.as_markup(),
        ],
    )

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

    await event.message.answer(
        text="Вот мои команды:",
        attachments=[
            builder.as_markup(),
        ],
    )
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

    await event.message.answer(
        text="Вот мои команды:",
        attachments=[
            builder.as_markup(),
        ],
    )
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
    await event.message.answer(text="Введите название категории:", attachments=[])
    await bot.delete_message(event.message.body.mid)

@dp.message_created(StateFilter(WAITING_CREATE_CATEGORY))
async def process_category_name(event: MessageCreated):
    chat_id = str(event.get_ids()[0])
    user_id = event.get_ids()[1]
    state = FSMContext(chat_id)
    cat = event.message.body.text

    await state.update_data({"new_category_name": cat})
    await state.set_state(WAITING_CATEGORY_DESCRIPTION)
    await event.message.answer(text="Введите описание категории:", attachments=[])

@dp.message_created(StateFilter(WAITING_CATEGORY_DESCRIPTION))
async def process_category_name(event: MessageCreated):
    chat_id = str(event.get_ids()[0])
    user_id = event.get_ids()[1]
    state = FSMContext(chat_id)
    description_cat = event.message.body.text
    cat = (await state.get_data()).get("new_category_name", "")

    category = category_service.create(user_id, cat, description_cat)

    await event.message.answer(f'Ваша новая категория "{cat}" создана!')
    await event.message.answer(
        text="Вот мои команды:",
        attachments=[
            builder.as_markup(),
        ],
    )
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
        await event.message.answer(
            text=f"Категория {payload.text} выбрана. Введите описание задачи:",
            attachments=[],
        )
        await bot.delete_message(event.message.body.mid)
    elif context == "manage_category":
        category_id = int(payload.foo)
        category = category_service.get_by_id(category_id)

        if not category:
            await event.message.answer(
                text="Категория не найдена",
                attachments=[]
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
    await event.message.answer(
        text="Введите новое название категории:",
        attachments=[]
    )
    await bot.delete_message(event.message.body.mid)

@dp.message_callback(CategoryActionButton.filter(F.action == "edit_desc"))
async def start_edit_category_description(event: MessageCallback, payload: CategoryActionButton):
    chat_id = str(event.get_ids()[0])
    state = FSMContext(chat_id)

    await state.update_data({"selected_category_id": payload.category_id})
    await state.set_state(WAITING_EDIT_CATEGORY_DESCRIPTION)
    await event.message.answer(
        text="Введите новое описание категории:",
        attachments=[]
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

    await event.message.answer(
        text="Вот мои команды:",
        attachments=[
            builder.as_markup(),
        ],
    )
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

    await event.message.answer(
        text="Вот мои команды:",
        attachments=[
            builder.as_markup(),
        ],
    )
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
    await event.message.answer(
        text="Вот мои команды:",
        attachments=[
            builder.as_markup(),
        ],
    )

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
