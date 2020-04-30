import secrets
from hashlib import sha256

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials, APIKeyCookie
from fastapi.templating import Jinja2Templates

from decorators import authorization
from globalvariables import SECRET_KEY, SESSION_TOKEN


class CustomRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.security = HTTPBasic(auto_error=False)
        self.secret_key = SECRET_KEY
        self.API_KEY = SESSION_TOKEN
        self.cookie_sec = APIKeyCookie(name=self.API_KEY, auto_error=False)
        self.templates = Jinja2Templates(directory="templates")

        self.user = {'login': 'trudnY', 'password': 'PaC13Nt'}


router = CustomRouter()


@router.get('/')
async def get_root():
    return {"message": "Hello World !"}


@router.get('/welcome')
@authorization.require_cookie_authorization(SESSION_TOKEN)
async def welcome(request: Request):
    response = router.templates.TemplateResponse('welcome.html', {'request': request, 'user': router.user['login']})
    return response


@router.post('/login')
async def login(credentials: HTTPBasicCredentials = Depends(router.security)):
    correct_username = secrets.compare_digest(credentials.username, router.user['login'])
    correct_password = secrets.compare_digest(credentials.password, router.user['password'])

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    session_token = sha256(str.encode(f"{credentials.username}:{router.secret_key}")).hexdigest()

    response = RedirectResponse(url='/welcome', status_code=status.HTTP_302_FOUND)
    response.set_cookie(key=router.API_KEY, value=session_token)

    # session = {'user': credentials.username, 'token': session_token}
    # tokens.append(session)

    return response


@router.post('/logout')
@authorization.require_cookie_authorization(SESSION_TOKEN)
async def logout(request: Request):
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(router.API_KEY)
    return response

