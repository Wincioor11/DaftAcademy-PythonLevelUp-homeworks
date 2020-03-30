from fastapi.testclient import TestClient
import pytest
from app import app

client = TestClient(app)

counter = 0


def test_hello():
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World during the coronavirus pandemic!"}


# @pytest.mark.parametrize('method', ['get', 'post', 'put', 'delete'])
def test_method():
    response = client.get('/method')
    assert response.status_code == 200
    assert response.json() == {"method": "GET"}


@pytest.mark.parametrize('patient', [{'name': 'John', 'surename': 'Kowalski'}, {'name': 'Żaneta', 'surename': 'Łaput'},
                                     {'name': 'v678%^&*UHGFR67uhgt67uko98hgef', 'surename': 'HablbaWW__loooll12(()\\'}])
def test_add_patient(patient):
    global counter
    counter += 1
    response = client.post('/patient', json=patient)
    assert response.status_code == 200
    assert response.json() == {"id": counter, "patient": patient}

