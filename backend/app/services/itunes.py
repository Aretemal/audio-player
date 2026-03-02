"""iTunes Search API — бесплатный поиск без ключа. https://developer.apple.com/library/archive/documentation/AudioVideo/Conceptual/iTuneSearchAPI/"""
import logging
from typing import Any, Dict, List

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

ITUNES_BASE = "https://itunes.apple.com/search"
ITUNES_LOOKUP = "https://itunes.apple.com/lookup"


def _proxy() -> str | None:
    return getattr(settings, "HTTPS_PROXY", None) or getattr(settings, "HTTP_PROXY", None)


async def search(
    query: str,
    entity: str,
    limit: int = 25,
    offset: int = 0,
) -> Dict[str, Any]:
    """entity: song | album | musicArtist"""
    if not query or not query.strip():
        return {"results": [], "count": 0, "total": 0, "offset": offset}
    params = {
        "term": query.strip(),
        "media": "music",
        "entity": entity,
        "limit": min(limit, 50),
        "offset": offset,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0, proxy=_proxy()) as client:
            resp = await client.get(ITUNES_BASE, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.ConnectError as e:
        logger.warning("iTunes search ConnectError: %s", e)
        return {"results": [], "count": 0, "total": 0, "offset": offset}
    except httpx.HTTPStatusError as e:
        logger.warning("iTunes search HTTP: status=%s", e.response.status_code)
        return {"results": [], "count": 0, "total": 0, "offset": offset}
    except Exception as e:
        logger.exception("iTunes search error: %s", e)
        return {"results": [], "count": 0, "total": 0, "offset": offset}

    results: List[Dict] = data.get("results", [])
    total = data.get("resultCount", len(results))
    return {"results": results, "count": len(results), "total": total, "offset": offset}


async def lookup_album(collection_id: str) -> Dict[str, Any]:
    """Получить данные альбома + треки по collectionId (iTunes)."""
    if not collection_id:
        return {"album": None, "tracks": []}
    params = {"id": str(collection_id), "entity": "song"}
    try:
        async with httpx.AsyncClient(timeout=12.0, proxy=_proxy()) as client:
            resp = await client.get(ITUNES_LOOKUP, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.ConnectError as e:
        logger.warning("iTunes lookup_album ConnectError: %s", e)
        return {"album": None, "tracks": []}
    except httpx.HTTPStatusError as e:
        logger.warning("iTunes lookup_album HTTP: status=%s", e.response.status_code)
        return {"album": None, "tracks": []}
    except Exception as e:
        logger.exception("iTunes lookup_album error: %s", e)
        return {"album": None, "tracks": []}

    results: List[Dict] = data.get("results", [])
    album = None
    tracks: List[Dict] = []
    for r in results:
        if r.get("wrapperType") == "collection":
            album = r
        if r.get("wrapperType") == "track":
            tracks.append(r)
    return {"album": album, "tracks": tracks}
