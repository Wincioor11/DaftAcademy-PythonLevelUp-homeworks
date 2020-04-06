from fastapi import FastAPI, Response, Request
from pydantic import BaseModel


app = FastAPI()

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
    global patients

    patient = AddPatientResp(id=len(patients), patient=patient)
    patients.append(patient)
    return patient


@app.get('/patient/{pk}')
def get_patient(pk: int):
    global patients

    patient_resp = next((patient for patient in patients if patient.id == pk), None)
    if patient_resp:
        return patient_resp.patient
    else:
        return Response(status_code=204)


@app.route('/method', methods=['Get', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def method(request: Request):
    return {"method": request.method}

