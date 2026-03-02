from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_user_from_request, verify_auth_global
from app.crud import playlist as playlist_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.playlist import PlaylistCreate, PlaylistRead, PlaylistUpdate

router = APIRouter(
    prefix="/playlists",
    tags=["playlists"],
    dependencies=[Depends(verify_auth_global)],
)


@router.get("/", response_model=list[PlaylistRead])
def list_playlists(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    playlists = playlist_crud.get_playlists_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    
    result = []
    for playlist in playlists:
        playlist_dict = {
            "id": playlist.id,
            "title": playlist.title,
            "description": playlist.description,
            "song_ids": [song.id for song in playlist.songs],
            "user_ids": [user.id for user in playlist.users],
            "created_at": playlist.created_at,
            "updated_at": playlist.updated_at,
        }
        result.append(PlaylistRead(**playlist_dict))
    return result


@router.post("/", response_model=PlaylistRead, status_code=status.HTTP_201_CREATED)
def create_playlist(
    playlist_in: PlaylistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    db_playlist = playlist_crud.create_playlist(db, playlist_in, user_id=current_user.id)
    
    return PlaylistRead(
        id=db_playlist.id,
        title=db_playlist.title,
        description=db_playlist.description,
        song_ids=[song.id for song in db_playlist.songs],
        user_ids=[user.id for user in db_playlist.users],
        created_at=db_playlist.created_at,
        updated_at=db_playlist.updated_at,
    )


@router.get("/{playlist_id}", response_model=PlaylistRead)
def get_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    db_playlist = playlist_crud.get_playlist(db, playlist_id)
    if not db_playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    
    if current_user not in db_playlist.users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    return PlaylistRead(
        id=db_playlist.id,
        title=db_playlist.title,
        description=db_playlist.description,
        song_ids=[song.id for song in db_playlist.songs],
        user_ids=[user.id for user in db_playlist.users],
        created_at=db_playlist.created_at,
        updated_at=db_playlist.updated_at,
    )


@router.put("/{playlist_id}", response_model=PlaylistRead)
def update_playlist(
    playlist_id: int,
    playlist_in: PlaylistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    db_playlist = playlist_crud.get_playlist(db, playlist_id)
    if not db_playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    
    if current_user not in db_playlist.users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    updated_playlist = playlist_crud.update_playlist(db, db_playlist, playlist_in)
    
    return PlaylistRead(
        id=updated_playlist.id,
        title=updated_playlist.title,
        description=updated_playlist.description,
        song_ids=[song.id for song in updated_playlist.songs],
        user_ids=[user.id for user in updated_playlist.users],
        created_at=updated_playlist.created_at,
        updated_at=updated_playlist.updated_at,
    )


@router.delete("/{playlist_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_playlist(
    playlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_user_from_request),
):
    db_playlist = playlist_crud.get_playlist(db, playlist_id)
    if not db_playlist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Playlist not found")
    
    if current_user not in db_playlist.users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    playlist_crud.delete_playlist(db, db_playlist)

