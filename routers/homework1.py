from fastapi import Response, Request, APIRouter
from pydantic import BaseModel


router = APIRouter()

patients = []


# @router.get('/')
# def hello():
#     return {"message": "Hello World during the coronavirus pandemic!"}


class AddPatientRq(BaseModel):
    name: str
    surename: str  # surname misspelled - on  purpose for testing with repl.it


class AddPatientResp(BaseModel):
    id: int
    patient: AddPatientRq


@router.post('/patient')
def add_patient(patient: AddPatientRq):
    global patients

    patient = AddPatientResp(id=len(patients), patient=patient)
    patients.append(patient)
    return patient


@router.get('/patient/{pk}')
def get_patient(pk: int):
    global patients

    patient_resp = next((patient for patient in patients if patient.id == pk), None)
    if patient_resp:
        return patient_resp.patient
    else:
        return Response(status_code=204)


@router.route('/method', methods=['Get', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def method(request: Request):
    return {"method": request.method}

