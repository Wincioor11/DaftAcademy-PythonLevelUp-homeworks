from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse


router = APIRouter()
router.secret_key = 'IK37DHYW92#0?PR1sOHR2311aQLR{[JNCREKCS1@LDNT6YHST389DV.A!1SGKJW4'  # 64 characters 'secret' key
user = {'login': 'trudnY', 'pass': 'PaC13Nt'}


@router.get('/welcome')
@router.get('/')
def welcome():
    return {"message": "Welcome to my world!"}


# class LoginRq(BaseModel):
#     login: str
#     password: str


@router.post('/login')
async def login(request: Request):
    form_body = await request.json()
    print(form_body)
    # login = ''
    # password = ''
    try:
        login = form_body['login']
        password = form_body['pass']
    except:
        raise HTTPException(status_code=400, detail="Missing login or pass fields in request body")

    if login == user['login'] and password == user['pass']:
        return RedirectResponse(url='/welcome', status_code=302)
        # return {"message": "POSZŁO!"}
    else:
        raise HTTPException(status_code=401, detail="Unoauthorized - provide correct login and pass")