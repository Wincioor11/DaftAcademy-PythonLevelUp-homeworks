from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

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
        raise HTTPException(status_code=204)  # Return HTTP 404 Not Found Error


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
