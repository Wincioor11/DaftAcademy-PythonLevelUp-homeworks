from pydantic import BaseModel


class AlbumModel(BaseModel):
	title: str
	artist_id: int