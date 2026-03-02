from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_user_from_request, verify_auth_global
from app.crud import bookmark as bookmark_crud
from app.db.session import get_db
from app.models.user import User
from app.models.bookmark import Bookmark
from app.schemas.bookmark import (
    BookmarkCreate,
    BookmarkRead,
    BookmarkUpdate,
    BookmarkCategoryCreate,
    BookmarkCategoryRead,
)

router = APIRouter(
    prefix="/bookmarks",
    tags=["bookmarks"],
    dependencies=[Depends(verify_auth_global)],
)


@router.get("/", response_model=List[BookmarkRead])
def list_bookmarks(
    bookmark_type: Optional[str] = Query(None, description="Тип закладки: artist или album"),
    category_id: Optional[int] = Query(None, description="ID категории"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    bookmarks = bookmark_crud.get_bookmarks_by_user(
        db, current_user.id, bookmark_type, category_id
    )
    return bookmarks


@router.post("/", response_model=BookmarkRead, status_code=201)
def create_bookmark(
    bookmark_in: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    bookmark = bookmark_crud.create_bookmark(db, bookmark_in, current_user.id)
    return bookmark


@router.get("/{bookmark_id}", response_model=BookmarkRead)
def get_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    bookmark = db.query(Bookmark).filter(
        Bookmark.id == bookmark_id,
        Bookmark.user_id == current_user.id
    ).first()
    
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    return bookmark


@router.put("/{bookmark_id}", response_model=BookmarkRead)
def update_bookmark(
    bookmark_id: int,
    bookmark_update: BookmarkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    bookmark = bookmark_crud.update_bookmark(
        db, bookmark_id, current_user.id, bookmark_update
    )
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    return bookmark


@router.delete("/{bookmark_id}", status_code=204)
def delete_bookmark(
    bookmark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    success = bookmark_crud.delete_bookmark(db, bookmark_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Bookmark not found")


@router.get("/check/{bookmark_type}/{musicbrainz_id}", response_model=Optional[BookmarkRead])
def check_bookmark(
    bookmark_type: str,
    musicbrainz_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    bookmark = bookmark_crud.get_bookmark_by_musicbrainz_id(
        db, current_user.id, musicbrainz_id, bookmark_type
    )
    return bookmark


@router.get("/categories/", response_model=List[BookmarkCategoryRead])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    categories = bookmark_crud.get_bookmark_categories(db, current_user.id)
    return categories


@router.post("/categories/", response_model=BookmarkCategoryRead, status_code=201)
def create_category(
    category_in: BookmarkCategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    category = bookmark_crud.create_bookmark_category(
        db, category_in.name, current_user.id
    )
    return category
