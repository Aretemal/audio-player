import logging
import time
from typing import Optional, List, Dict, Any
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class MusicBrainzService:
    BASE_URL = "https://musicbrainz.org/ws/2"
    USER_AGENT = f"{settings.PROJECT_NAME}/1.0.0 (contact@example.com)"
    _last_request_time = 0
    _min_request_interval = 1.0

    @classmethod
    def _proxy(cls) -> str | None:
        return getattr(settings, "HTTPS_PROXY", None) or getattr(settings, "HTTP_PROXY", None)

    @classmethod
    def _rate_limit(cls):
        current_time = time.time()
        time_since_last = current_time - cls._last_request_time
        if time_since_last < cls._min_request_interval:
            time.sleep(cls._min_request_interval - time_since_last)
        cls._last_request_time = time.time()
    
    @classmethod
    async def search_artist(
        cls,
        query: str = "",
        limit: int = 25,
        offset: int = 0
    ) -> Dict[str, Any]:
        cls._rate_limit()
        url = f"{cls.BASE_URL}/artist"
        if not query or query.strip() == "":
            query = "type:group OR type:person"
        
        params = {
            "query": query.strip(),
            "limit": min(limit, 100),
            "offset": offset,
            "fmt": "json"
        }
        
        headers = {
            "User-Agent": cls.USER_AGENT,
            "Accept": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0, proxy=cls._proxy()) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                artists = []
                for artist in data.get("artists", []):
                    artist_data = {
                        "id": artist.get("id"),
                        "name": artist.get("name"),
                        "type": artist.get("type"),
                        "country": artist.get("country"),
                        "disambiguation": artist.get("disambiguation"),
                        "life_span": artist.get("life-span", {}),
                        "tags": [tag.get("name") for tag in artist.get("tags", [])[:5]],
                    }
                    artists.append(artist_data)
                
                return {
                    "artists": artists,
                    "count": len(artists),
                    "total": data.get("count", 0),
                    "offset": offset
                }
        except httpx.ConnectError as e:
            cause = getattr(e, "__cause__", None)
            logger.warning(
                "MusicBrainz search_artist: нет связи с сервером (ConnectError). Проверьте интернет, фаервол, прокси. %s",
                cause or e,
            )
            return {"artists": [], "count": 0, "total": 0, "offset": offset}
        except httpx.HTTPStatusError as e:
            body = (e.response.text or "")[:500]
            logger.warning(
                "MusicBrainz search_artist HTTP error: status=%s url=%s body=%s",
                e.response.status_code, e.request.url, body
            )
            return {"artists": [], "count": 0, "total": 0, "offset": offset}
        except httpx.HTTPError as e:
            logger.warning("MusicBrainz search_artist HTTP error: %s", type(e).__name__, exc_info=True)
            return {"artists": [], "count": 0, "total": 0, "offset": offset}
        except Exception as e:
            logger.exception("MusicBrainz search_artist error: %s %r", type(e).__name__, e)
            return {"artists": [], "count": 0, "total": 0, "offset": offset}
    
    @classmethod
    async def get_artist_by_id(
        cls,
        artist_id: str
    ) -> Optional[Dict[str, Any]]:
        cls._rate_limit()
        url = f"{cls.BASE_URL}/artist/{artist_id}"
        params = {
            "inc": "tags+ratings+aliases+releases+recordings",
            "fmt": "json"
        }
        
        headers = {
            "User-Agent": cls.USER_AGENT,
            "Accept": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0, proxy=cls._proxy()) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                releases = []
                for release in data.get("releases", [])[:20]:
                    releases.append({
                        "id": release.get("id"),
                        "title": release.get("title"),
                        "date": release.get("date"),
                        "status": release.get("status"),
                    })
                recordings = []
                for recording in data.get("recordings", [])[:20]:
                    recordings.append({
                        "id": recording.get("id"),
                        "title": recording.get("title"),
                        "length": recording.get("length"),
                    })
                
                return {
                    "id": data.get("id"),
                    "name": data.get("name"),
                    "type": data.get("type"),
                    "country": data.get("country"),
                    "disambiguation": data.get("disambiguation"),
                    "life_span": data.get("life-span", {}),
                    "aliases": [alias.get("name") for alias in data.get("aliases", [])],
                    "tags": [{"name": tag.get("name"), "count": tag.get("count", 0)} for tag in data.get("tags", [])],
                    "releases": releases,
                    "recordings": recordings,
                }
        except httpx.HTTPError as e:
            print(f"MusicBrainz API error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error getting artist info: {e}")
            return None
    
    @classmethod
    async def get_release_by_id(
        cls,
        release_id: str
    ) -> Optional[Dict[str, Any]]:
        cls._rate_limit()
        url = f"{cls.BASE_URL}/release/{release_id}"
        params = {
            "inc": "artists+recordings+media",
            "fmt": "json"
        }
        
        headers = {
            "User-Agent": cls.USER_AGENT,
            "Accept": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0, proxy=cls._proxy()) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                artists = []
                for artist_credit in data.get("artist-credit", []):
                    if "artist" in artist_credit:
                        artists.append({
                            "id": artist_credit["artist"].get("id"),
                            "name": artist_credit["artist"].get("name"),
                        })
                tracks = []
                for medium in data.get("media", []):
                    for track in medium.get("tracks", []):
                        recording = track.get("recording", {})
                        tracks.append({
                            "id": recording.get("id"),
                            "title": recording.get("title"),
                            "length": recording.get("length"),
                            "position": track.get("position"),
                        })
                
                return {
                    "id": data.get("id"),
                    "title": data.get("title"),
                    "artists": artists,
                    "date": data.get("date"),
                    "country": data.get("country"),
                    "barcode": data.get("barcode"),
                    "status": data.get("status"),
                    "tracks": tracks,
                }
        except httpx.HTTPError as e:
            print(f"MusicBrainz API error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error getting release info: {e}")
            return None

    @classmethod
    async def search_release(
        cls,
        query: str = "",
        limit: int = 25,
        offset: int = 0
    ) -> Dict[str, Any]:
        if not query or not query.strip():
            return {"releases": [], "count": 0, "total": 0, "offset": offset}
        cls._rate_limit()
        url = f"{cls.BASE_URL}/release"
        params = {
            "query": query.strip(),
            "limit": min(limit, 100),
            "offset": offset,
            "fmt": "json"
        }
        headers = {
            "User-Agent": cls.USER_AGENT,
            "Accept": "application/json"
        }
        try:
            async with httpx.AsyncClient(timeout=10.0, proxy=cls._proxy()) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                releases = []
                for r in data.get("releases", []):
                    artist_name = ""
                    if "artist-credit" in r and r["artist-credit"]:
                        artist_name = r["artist-credit"][0].get("artist", {}).get("name", "")
                    releases.append({
                        "id": r.get("id"),
                        "title": r.get("title"),
                        "date": r.get("date"),
                        "artist": artist_name,
                        "status": r.get("status"),
                    })
                return {
                    "releases": releases,
                    "count": len(releases),
                    "total": data.get("count", 0),
                    "offset": offset,
                }
        except httpx.ConnectError as e:
            cause = getattr(e, "__cause__", None)
            logger.warning(
                "MusicBrainz search_release: нет связи с сервером (ConnectError). Проверьте интернет, фаервол, прокси. %s",
                cause or e,
            )
            return {"releases": [], "count": 0, "total": 0, "offset": offset}
        except httpx.HTTPStatusError as e:
            body = (e.response.text or "")[:500]
            logger.warning(
                "MusicBrainz search_release HTTP error: status=%s url=%s body=%s",
                e.response.status_code, e.request.url, body
            )
            return {"releases": [], "count": 0, "total": 0, "offset": offset}
        except httpx.HTTPError as e:
            logger.warning("MusicBrainz search_release HTTP error: %s", type(e).__name__, exc_info=True)
            return {"releases": [], "count": 0, "total": 0, "offset": offset}
        except Exception as e:
            logger.exception("MusicBrainz search_release error: %s %r", type(e).__name__, e)
            return {"releases": [], "count": 0, "total": 0, "offset": offset}

    @classmethod
    async def search_recording(
        cls,
        query: str = "",
        limit: int = 25,
        offset: int = 0,
    ) -> Dict[str, Any]:
        if not query or not query.strip():
            return {"recordings": [], "count": 0, "total": 0, "offset": offset}
        cls._rate_limit()
        url = f"{cls.BASE_URL}/recording"
        params = {
            "query": query.strip(),
            "limit": min(limit, 100),
            "offset": offset,
            "fmt": "json",
        }
        headers = {"User-Agent": cls.USER_AGENT, "Accept": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=10.0, proxy=cls._proxy()) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                recordings = []
                for r in data.get("recordings", []):
                    artist_name = ""
                    ac = r.get("artist-credit") or []
                    if ac and isinstance(ac[0], dict):
                        artist_name = ac[0].get("artist", {}).get("name") or ac[0].get("name") or ""
                    elif ac:
                        artist_name = str(ac[0]) if ac else ""
                    length_ms = r.get("length")
                    recordings.append({
                        "id": r.get("id"),
                        "title": r.get("title"),
                        "artist": artist_name,
                        "length": length_ms,
                        "preview_url": None,
                    })
                return {
                    "recordings": recordings,
                    "count": len(recordings),
                    "total": data.get("count", 0),
                    "offset": offset,
                }
        except httpx.ConnectError as e:
            cause = getattr(e, "__cause__", None)
            logger.warning(
                "MusicBrainz search_recording ConnectError: %s", cause or e,
            )
            return {"recordings": [], "count": 0, "total": 0, "offset": offset}
        except httpx.HTTPStatusError as e:
            logger.warning(
                "MusicBrainz search_recording HTTP: status=%s", e.response.status_code,
            )
            return {"recordings": [], "count": 0, "total": 0, "offset": offset}
        except Exception as e:
            logger.exception("MusicBrainz search_recording error: %s %r", type(e).__name__, e)
            return {"recordings": [], "count": 0, "total": 0, "offset": offset}
