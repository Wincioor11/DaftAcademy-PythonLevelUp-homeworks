from fastapi import FastAPI, Response, status
from pydantic import BaseModel
import json

from starlette.responses import JSONResponse

app = FastAPI()

counter: int = 0
patients = []


@app.get('/')
def hello():
    return {"message": "Hello World during the coronavirus pandemic!"}


class AddPatientRq(BaseModel):
    name: str
    surename: str  # surname misspelled - on  purpose for testing with repl.it


class AddPatientResp(BaseModel):
    id: int
    patient: AddPatientRq


@app.post('/patient')
def add_patient(patient: AddPatientRq):
    global counter, patients
    counter += 1
    patient = AddPatientResp(id=counter, patient=patient)
    patients.append(patient)
    return patient


class GetPatientResp(BaseModel):
    name: str
    surename: str


@app.get('/patient/{pk}')
def get_patient(pk: int):
    global patients
    patient_resp = next((patient for patient in patients if patient.id == pk), None)
    if patient_resp:
        return GetPatientResp(name=patient_resp.patient.name, surename=patient_resp.patient.surename)
    else:

        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"message": "204 - Not Found"})  # Return HTTP 204 No Content


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
