"""
Эндпоинты для работы с исполнителями через MusicBrainz API
"""
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from app.auth.dependencies import verify_auth_global
from app.services.musicbrainz import MusicBrainzService

router = APIRouter(
    prefix="/artists",
    tags=["artists"],
    dependencies=[Depends(verify_auth_global)],
)


@router.get("/")
async def list_artists(
    q: str = Query("", description="Поисковый запрос (имя исполнителя). Если пусто, возвращает популярных"),
    limit: int = Query(25, ge=1, le=100, description="Количество результатов"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
):
    """
    Получение списка исполнителей из MusicBrainz
    
    Если запрос пустой, возвращает популярных исполнителей.
    """
    results = await MusicBrainzService.search_artist(
        query=q,
        limit=limit,
        offset=offset
    )
    
    return results


@router.get("/{artist_id}")
async def get_artist(
    artist_id: str,
):
    """
    Получение детальной информации об исполнителе по MusicBrainz ID
    Включает список песен и альбомов
    """
    result = await MusicBrainzService.get_artist_by_id(artist_id)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Artist not found"
        )
    
    return result


@router.get("/{artist_id}/recordings")
async def get_artist_recordings(
    artist_id: str,
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Получение списка записей (песен) исполнителя
    """
    MusicBrainzService._rate_limit()
    
    url = f"{MusicBrainzService.BASE_URL}/recording"
    params = {
        "query": f"arid:{artist_id}",
        "limit": limit,
        "offset": offset,
        "fmt": "json"
    }
    
    headers = {
        "User-Agent": MusicBrainzService.USER_AGENT,
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            recordings = []
            for recording in data.get("recordings", []):
                recordings.append({
                    "id": recording.get("id"),
                    "title": recording.get("title"),
                    "length": recording.get("length"),
                })
            
            return {
                "recordings": recordings,
                "count": len(recordings),
                "total": data.get("count", 0),
                "offset": offset
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching recordings: {str(e)}"
        )


@router.get("/{artist_id}/releases")
async def get_artist_releases(
    artist_id: str,
    limit: int = Query(100, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Получение списка релизов (альбомов) исполнителя
    """
    MusicBrainzService._rate_limit()
    
    url = f"{MusicBrainzService.BASE_URL}/release"
    params = {
        "query": f"arid:{artist_id}",
        "limit": limit,
        "offset": offset,
        "fmt": "json"
    }
    
    headers = {
        "User-Agent": MusicBrainzService.USER_AGENT,
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            releases = []
            for release in data.get("releases", []):
                releases.append({
                    "id": release.get("id"),
                    "title": release.get("title"),
                    "date": release.get("date"),
                    "status": release.get("status"),
                })
            
            return {
                "releases": releases,
                "count": len(releases),
                "total": data.get("count", 0),
                "offset": offset
            }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching releases: {str(e)}"
        )
