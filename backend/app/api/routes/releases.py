"""
Эндпоинты для работы с релизами (альбомами) через MusicBrainz API
"""
from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import verify_auth_global
from app.services.musicbrainz import MusicBrainzService

router = APIRouter(
    prefix="/releases",
    tags=["releases"],
    dependencies=[Depends(verify_auth_global)],
)


@router.get("/{release_id}")
async def get_release(
    release_id: str,
):
    """
    Получение детальной информации о релизе (альбоме) по MusicBrainz ID
    Включает список треков
    """
    result = await MusicBrainzService.get_release_by_id(release_id)
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Release not found"
        )
    
    return result
