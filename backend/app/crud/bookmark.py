from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.bookmark import Bookmark, BookmarkCategory
from app.schemas.bookmark import BookmarkCreate, BookmarkUpdate


def get_bookmark_by_musicbrainz_id(
    db: Session,
    user_id: int,
    musicbrainz_id: str,
    bookmark_type: str
) -> Optional[Bookmark]:
    return db.query(Bookmark).filter(
        Bookmark.user_id == user_id,
        Bookmark.musicbrainz_id == musicbrainz_id,
        Bookmark.bookmark_type == bookmark_type
    ).first()


def create_bookmark(
    db: Session,
    bookmark_in: BookmarkCreate,
    user_id: int
) -> Bookmark:
    existing = get_bookmark_by_musicbrainz_id(
        db, user_id, bookmark_in.musicbrainz_id, bookmark_in.bookmark_type
    )
    if existing:
        return existing
    
    db_bookmark = Bookmark(
        user_id=user_id,
        bookmark_type=bookmark_in.bookmark_type,
        musicbrainz_id=bookmark_in.musicbrainz_id,
        title=bookmark_in.title,
        extra_data=bookmark_in.extra_data,
    )

    if bookmark_in.category_ids:
        categories = db.query(BookmarkCategory).filter(
            BookmarkCategory.id.in_(bookmark_in.category_ids)
        ).all()
        db_bookmark.categories = categories
    
    db.add(db_bookmark)
    db.commit()
    db.refresh(db_bookmark)
    return db_bookmark


def get_bookmarks_by_user(
    db: Session,
    user_id: int,
    bookmark_type: Optional[str] = None,
    category_id: Optional[int] = None
) -> List[Bookmark]:
    query = db.query(Bookmark).filter(Bookmark.user_id == user_id)
    
    if bookmark_type:
        query = query.filter(Bookmark.bookmark_type == bookmark_type)
    
    if category_id:
        query = query.join(Bookmark.categories).filter(
            BookmarkCategory.id == category_id
        )
    
    return query.all()


def delete_bookmark(db: Session, bookmark_id: int, user_id: int) -> bool:
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == user_id
    ).first()
    
    if not bookmark:
        return False
    
    db.delete(bookmark)
    db.commit()
    return True


def update_bookmark(
    db: Session,
    bookmark_id: int,
    user_id: int,
    bookmark_update: BookmarkUpdate
) -> Optional[Bookmark]:
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == user_id
    ).first()
    
    if not bookmark:
        return None
    
    if bookmark_update.title is not None:
        bookmark.title = bookmark_update.title
    if bookmark_update.extra_data is not None:
        bookmark.extra_data = bookmark_update.extra_data
    if bookmark_update.category_ids is not None:
        categories = db.query(BookmarkCategory).filter(
            BookmarkCategory.id.in_(bookmark_update.category_ids)
        ).all()
        bookmark.categories = categories
    
    db.commit()
    db.refresh(bookmark)
    return bookmark



def create_bookmark_category(
    db: Session,
    name: str,
    user_id: Optional[int] = None
) -> BookmarkCategory:
    db_category = BookmarkCategory(
        name=name,
        is_default=False,
        user_id=user_id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def get_bookmark_categories(
    db: Session,
    user_id: Optional[int] = None
) -> List[BookmarkCategory]:
    query = db.query(BookmarkCategory)

    if user_id is None:
        query = query.filter(BookmarkCategory.is_default == True)
    else:
        query = query.filter(
            (BookmarkCategory.is_default == True) |
            (BookmarkCategory.user_id == user_id)
        )
    
    return query.all()


def get_default_categories(db: Session) -> List[BookmarkCategory]:
    return db.query(BookmarkCategory).filter(
        BookmarkCategory.is_default == True
    ).all()
