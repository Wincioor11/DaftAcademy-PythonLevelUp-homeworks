import secrets
from hashlib import sha256

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates

from decorators import authorization
from globalvariables import SECRET_KEY, SESSION_TOKEN

router = APIRouter()
router.secret_key = SECRET_KEY  # 64 characters 'secret' key

user = {'login': 'trudnY', 'password': 'PaC13Nt'}

security = HTTPBasic()

templates = Jinja2Templates(directory="templates")


@router.get('/welcome')
@router.get('/')
@authorization.require_cookie_authorization(SESSION_TOKEN)
async def welcome(request: Request):
    response = templates.TemplateResponse('welcome.html', {'request': request, 'user': user['login']})
    return response


@router.post('/login')
async def login(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, user['login'])
    correct_password = secrets.compare_digest(credentials.password, user['password'])

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    session_token = sha256(str.encode(f"{credentials.username}:{router.secret_key}")).hexdigest()

    response = RedirectResponse(url='/welcome', status_code=status.HTTP_302_FOUND)
    response.set_cookie(key=SESSION_TOKEN, value=session_token)

    # session = {'user': credentials.username, 'token': session_token}
    # tokens.append(session)

    return response


@router.post('/logout')
@authorization.require_cookie_authorization(SESSION_TOKEN)
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(SESSION_TOKEN)
    return response

