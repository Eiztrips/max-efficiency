from app.models import Category


def _positive_int_validator(value: int, field_name: str):
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{field_name} должен быть положительным целым числом.")

def _not_empty_str_validator(value: str, field_name: str):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} должен быть непустой строкой.")

def _not_empty_dict_validator(value: dict, field_name: str):
    if not isinstance(value, dict) or not value:
        raise ValueError(f"{field_name} должен быть непустым словарем.")

def _dict_keys_constant_validator(data: dict, constant_keys: set[str]):
    for key in constant_keys:
        if key in data:
            raise ValueError(f"Нельзя изменять поле: {key}")

def _category_exists_validator(category: Category):
    if not category:
        raise ValueError("Категория не найдена")

def _user_exists_validator(user):
    if not user:
        raise ValueError("Пользователь не найден")