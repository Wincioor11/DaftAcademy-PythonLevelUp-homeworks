import pytest
from fastapi.testclient import TestClient

from app import app

client = TestClient(app)

counter = 0


# def test_hello():
#     response = client.get('/')
#     assert response.status_code == 200
#     assert response.json() == {"message": "Hello World during the coronavirus pandemic!"}


# @pytest.mark.parametrize('method', ['get', 'post', 'put', 'delete'])
def test_method():
    response = client.get('/method')
    assert response.status_code == 200
    assert response.json() == {"method": "GET"}


@pytest.mark.parametrize('patient', [
                                    {'name': 'John', 'surename': 'Kowalski'},
                                    {'name': 'Żaneta', 'surename': 'Łaput'},
                                    {'name': 'v678%^&*UHGFR67uhgt67uko98hgef', 'surename': 'HablbaWW__loooll12(()\\'}
                                    ])
def test_add_patient(patient):
    global counter

    response = client.post('/patient', json=patient)
    assert response.status_code == 200
    assert response.json() == {"id": counter, "patient": patient}
    counter += 1


@pytest.mark.parametrize('pk, patient', [
                                    pytest.param(1, {'name': 'John', 'surename': 'Kowalski'}),
                                    pytest.param(2, {'name': 'Żaneta', 'surename': 'Łaput'}),
                                    pytest.param(3, {'name': 'v678%^&*UHGFR67uhgt67uko98hgef', 'surename': 'HablbaWW__loooll12(()\\'})
                                    ])
def test_get_patient(pk, patient):
    # client.post('/patient', json=patient)
    response = client.get(f'/patient/{pk}')
    assert response.status_code == 200
    assert response.json() == {"name": patient['name'], "surename": patient['surename']}
