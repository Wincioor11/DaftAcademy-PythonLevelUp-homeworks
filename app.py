from fastapi import FastAPI
from pydantic import BaseModel, ValidationError

app = FastAPI()

counter: int = 0


@app.get('/')
def hello():
    return {"message": "Hello World during the coronavirus pandemic!"}


class AddPatientRq(BaseModel):
    name: str
    surename: str


class AddPatientResp(BaseModel):
    id: int
    patient: AddPatientRq


@app.post('/patient')
def add_patient(patient: AddPatientRq):
    global counter
    counter += 1
    return AddPatientResp(id=counter, patient=patient)


@app.get('/method')
def method():
    return {"method": "GET"}


@app.post('/method')
def method():
    return {"method": "POST"}


@app.put('/method')
def method():
    return {"method": "PUT"}


@app.delete('/method')
def method():
    return {"method": "DELETE"}
