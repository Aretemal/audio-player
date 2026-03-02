# Backend (FastAPI)

## Setup

```bash
cd backend
python -m venv venv

# Активация виртуального окружения:
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
venv\Scripts\activate.bat
# Git Bash / Linux / Mac:
source venv/Scripts/activate

# Установка зависимостей:
pip install -r requirements.txt
```

## Environment

1. Скопируйте `env.example` в `.env` и при необходимости отредактируйте значения.
2. По умолчанию используется SQLite файл `app.db` в корне backend.
3. Если запросы к MusicBrainz (поиск исполнителей/альбомов) не проходят из-за фаервола или прокси, задайте в `.env` переменные `HTTP_PROXY` или `HTTPS_PROXY` (например: `HTTPS_PROXY=http://proxy:3128`).

## Running

```bash
cd backend
uvicorn app.main:app --reload
```

API будет доступно по адресу http://localhost:8000, документация — http://localhost:8000/docs.

## Tests

```bash
cd backend
pytest
```

