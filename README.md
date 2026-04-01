# HH Analytics MVP

MVP-проект с backend на FastAPI и frontend на React для аналитики вакансий HH по двум трекам:
- `Python backend`
- `Swift`

Показываются ключевые метрики:
- Количество вакансий
- Средняя зарплата в RUR по бакетам опыта (`0`, `1-3`, `3-6`, `6+`)
- Покрытие зарплатой

## Стек

- Backend: FastAPI, SQLAlchemy, PostgreSQL, APScheduler, Alembic
- Frontend: React + TypeScript + Recharts (Vite)
- Инфраструктура: Docker Compose

## Быстрый старт

```bash
docker compose up --build
```

Сервисы:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/v1
- Swagger: http://localhost:8000/docs

## API

- `GET /api/v1/health`
- `POST /api/v1/sync?track=python_backend|swift|all`
- `GET /api/v1/metrics/latest?track=python_backend|swift`
- `GET /api/v1/metrics/history?track=python_backend|swift&days=30`

## Локальная разработка

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Тесты

```bash
cd backend
pytest

cd ../frontend
npm test
```
