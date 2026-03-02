import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.main import api_router
from app.core.config import settings
from app.db import base  # noqa: F401
from app.db.session import Base, engine


def create_tables():
    Base.metadata.create_all(bind=engine)


def create_application() -> FastAPI:
    application = FastAPI(title=settings.PROJECT_NAME)

    application.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2[0-9]|3[01])\.\d+\.\d+):\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    application.mount(f"/{settings.UPLOAD_DIR_NAME}", StaticFiles(directory=str(upload_dir)), name="uploads")
    
    application.include_router(api_router)
    return application


app = create_application()


@app.on_event("startup")
def on_startup():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("app.api.routes.search").setLevel(logging.INFO)
    create_tables()
    from app.db.session import SessionLocal
    from app.crud import bookmark as bookmark_crud
    from app.models.bookmark import BookmarkCategory
    
    db = SessionLocal()
    try:
        default_categories = db.query(BookmarkCategory).filter(
            BookmarkCategory.is_default == True
        ).all()
        
        if not default_categories:
            categories = [
                "Favorites",
                "To listen",
                "Loved",
            ]
            for category_name in categories:
                bookmark_crud.create_bookmark_category(db, category_name, None)
                category = db.query(BookmarkCategory).filter(
                    BookmarkCategory.name == category_name,
                    BookmarkCategory.user_id == None
                ).first()
                if category:
                    category.is_default = True
            db.commit()
    except Exception as e:
        print(f"Error initializing default bookmark categories: {e}")
        db.rollback()
    finally:
        db.close()