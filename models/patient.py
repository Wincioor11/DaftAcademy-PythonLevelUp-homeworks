from pydantic import BaseModel


class PatientModel(BaseModel):
    name: str
    surname: str