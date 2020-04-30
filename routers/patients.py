from fastapi import Response, Request, APIRouter
from fastapi.responses import RedirectResponse

from decorators import authorization
from globalvariables import SESSION_TOKEN
from models.patient import PatientModel

router = APIRouter()

# patients = []
patients = {}


# @router.get('/')
# def hello():
#     return {"message": "Hello World during the coronavirus pandemic!"}



@router.post('/patient')
@authorization.require_cookie_authorization(SESSION_TOKEN)
async def add_patient(request: Request, patient: PatientModel):
    global patients

    # new_patient = PatientResponseModel(id=len(patients), patient=patient)
    # patients.append(new_patient)
    if len(patients.keys()) == 0:
        new_id = 0
    else:
        new_id = max(patients.keys()) + 1

    patients[new_id] = patient

    response = RedirectResponse(url=f'/patient/{new_id}', status_code=302)
    return response


@router.get('/patient')
@authorization.require_cookie_authorization(SESSION_TOKEN)
async def get_patients(request: Request):
    """Returns dict of patients as JSON"""
    return patients


@router.get('/patient/{pk}')
@authorization.require_cookie_authorization(SESSION_TOKEN)
async def get_patient(request: Request, pk: int):
    # patient_resp = next((patient for patient in patients if patient.id == pk), None)

    if pk in patients.keys():
        return patients[pk]
    else:
        return Response(status_code=204)


@router.delete('/patient/{pk}')
@authorization.require_cookie_authorization(SESSION_TOKEN)
async def delete_patient(request: Request, pk: int):
    global patients

    if pk in patients.keys():
        del patients[pk]

    return Response(status_code=204)


# @router.route('/method', methods=['Get', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
# async def method(request: Request):
#     return {"method": request.method}

