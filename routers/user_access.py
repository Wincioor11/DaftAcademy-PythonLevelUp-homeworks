from fastapi import APIRouter

router = APIRouter()


@router.get('/welcome')
@router.get('/')
def welcome():
    return {"message": "Welcome to my world!"}



