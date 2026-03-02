"""Deezer API — поиск без авторизации. https://developers.deezer.com/api"""
import logging
from typing import Any, Dict, List

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

DEEZER_BASE = "https://api.deezer.com"


def _proxy() -> str | None:
    return getattr(settings, "HTTPS_PROXY", None) or getattr(settings, "HTTP_PROXY", None)


async def search_track(query: str, limit: int = 25, offset: int = 0) -> Dict[str, Any]:
    if not query or not query.strip():
        return {"data": [], "total": 0, "offset": offset}
    try:
        async with httpx.AsyncClient(timeout=10.0, proxy=_proxy()) as client:
            resp = await client.get(
                f"{DEEZER_BASE}/search/track",
                params={"q": query.strip(), "limit": min(limit, 25), "index": offset},
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.ConnectError as e:
        logger.warning("Deezer search_track ConnectError: %s", e)
        return {"data": [], "total": 0, "offset": offset}
    except httpx.HTTPStatusError as e:
        logger.warning("Deezer search_track HTTP: status=%s", e.response.status_code)
        return {"data": [], "total": 0, "offset": offset}
    except Exception as e:
        logger.exception("Deezer search_track error: %s", e)
        return {"data": [], "total": 0, "offset": offset}
    tracks: List[Dict] = data.get("data", [])
    total = data.get("total", len(tracks))
    return {"data": tracks, "total": total, "offset": offset}


async def search_album(query: str, limit: int = 25, offset: int = 0) -> Dict[str, Any]:
    if not query or not query.strip():
        return {"data": [], "total": 0, "offset": offset}
    try:
        async with httpx.AsyncClient(timeout=10.0, proxy=_proxy()) as client:
            resp = await client.get(
                f"{DEEZER_BASE}/search/album",
                params={"q": query.strip(), "limit": min(limit, 25), "index": offset},
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.ConnectError as e:
        logger.warning("Deezer search_album ConnectError: %s", e)
        return {"data": [], "total": 0, "offset": offset}
    except Exception as e:
        logger.exception("Deezer search_album error: %s", e)
        return {"data": [], "total": 0, "offset": offset}
    albums: List[Dict] = data.get("data", [])
    return {"data": albums, "total": data.get("total", len(albums)), "offset": offset}


async def search_artist(query: str, limit: int = 25, offset: int = 0) -> Dict[str, Any]:
    if not query or not query.strip():
        return {"data": [], "total": 0, "offset": offset}
    try:
        async with httpx.AsyncClient(timeout=10.0, proxy=_proxy()) as client:
            resp = await client.get(
                f"{DEEZER_BASE}/search/artist",
                params={"q": query.strip(), "limit": min(limit, 25), "index": offset},
            )
            resp.raise_for_status()
            data = resp.json()
    except httpx.ConnectError as e:
        logger.warning("Deezer search_artist ConnectError: %s", e)
        return {"data": [], "total": 0, "offset": offset}
    except Exception as e:
        logger.exception("Deezer search_artist error: %s", e)
        return {"data": [], "total": 0, "offset": offset}
    artists: List[Dict] = data.get("data", [])
    return {"data": artists, "total": data.get("total", len(artists)), "offset": offset}


async def get_album(album_id: str) -> Dict[str, Any]:
    """Детали альбома + треки (Deezer)."""
    if not album_id:
        return {}
    try:
        async with httpx.AsyncClient(timeout=12.0, proxy=_proxy()) as client:
            resp = await client.get(f"{DEEZER_BASE}/album/{album_id}")
            resp.raise_for_status()
            return resp.json()
    except httpx.ConnectError as e:
        logger.warning("Deezer get_album ConnectError: %s", e)
        return {}
    except httpx.HTTPStatusError as e:
        logger.warning("Deezer get_album HTTP: status=%s", e.response.status_code)
        return {}
    except Exception as e:
        logger.exception("Deezer get_album error: %s", e)
        return {}
