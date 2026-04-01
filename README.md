# Shop — Лабораторная работа по ООП

CLI-приложение для управления магазином: клиенты, товары, склад, заказы.

## Архитектура

```
domain/           — бизнес-сущности, валидация, исключения, стратегии скидок
repository/       — абстракция хранилища + реализации (InMemory, PostgreSQL)
service/          — бизнес-логика (CustomerService, ProductService, OrderService)
presentation/     — CLI-интерфейс
db.py             — подключение к PostgreSQL (SQLAlchemy)
main.py           — точка входа
```

Зависимости между слоями:
```
presentation → service → repository → domain
```

## Установка

```bash
python -m venv oop_venv
source oop_venv/bin/activate
pip install -r requirements.txt
```

## Настройка PostgreSQL

```bash
# Через Docker (рекомендуется)
docker run -d \
  --name shop_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=shop_db \
  -p 5432:5432 \
  postgres:16
```

Создать `.env` из шаблона:
```bash
cp .env.example .env
```

`.env`:
```
DB_URL=postgresql://postgres:postgres@localhost:5432/shop_db
```

## Миграции

```bash
# Применить все миграции
alembic upgrade head

# Откатить последнюю
alembic downgrade -1
```

## Запуск

```bash
python main.py
```

## Тесты

```bash
pytest tests/ -v
pytest tests/ --cov=domain --cov-report=term-missing
```
