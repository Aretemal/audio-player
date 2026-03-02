from fastapi import APIRouter

from app.api.routes import albums, artists, auth, bookmarks, playlists, releases, search, songs
from app.core.config import settings

api_router = APIRouter(prefix=settings.API_V1_STR)

api_router.include_router(auth.router)
api_router.include_router(songs.router)
api_router.include_router(albums.router)
api_router.include_router(playlists.router)
api_router.include_router(search.router)
api_router.include_router(artists.router)
api_router.include_router(releases.router)
api_router.include_router(bookmarks.router)