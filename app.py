import secrets
from typing import Dict

import aiosqlite as aiosqlite
import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import RedirectResponse, Response
from fastapi.security import HTTPBasic, APIKeyCookie, HTTPBasicCredentials
from starlette.templating import Jinja2Templates

from globalvariables import SESSION_TOKEN, SECRET_KEY
# from routers import patients, user_access
from models.album import AlbumModel
from models.customer import CustomerModel
from models.patient import PatientModel


class DaftAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.counter: int = 0
        self.patients: Dict[int, PatientModel] = {}
        self.security = HTTPBasic(auto_error=False)
        self.secret_key = SECRET_KEY
        self.API_KEY = SESSION_TOKEN
        self.cookie_sec = APIKeyCookie(name=self.API_KEY, auto_error=False)
        self.templates = Jinja2Templates(directory="templates")

        self.user = {'login': 'trudnY', 'password': 'PaC13Nt'}


app = DaftAPI()


# app.include_router(patients.router, tags=['endpoints for homework1'])
# app.include_router(user_access.router, tags=['endpoints for user access'])


def is_logged(session: str = Depends(app.cookie_sec), silent: bool = False):
    try:
        payload = jwt.decode(session, app.secret_key)
        return payload.get(app.API_KEY)
    except Exception as e:
        print(e)

    if silent:
        return False

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


# def authethicate(credentials: Optional[HTTPBasicCredentials] = Depends(app.security)):
#     if not credentials:
#         return False
#
#     correct_username = secrets.compare_digest(credentials.username, app.user['login'])
#     correct_password = secrets.compare_digest(credentials.password,  app.user['password'])
#
#     if not (correct_username and correct_password):
#         return False
#     return True


@app.on_event("startup")
async def startup():
    app.db_connection = await aiosqlite.connect('data/chinook/chinook.db')


@app.on_event("shutdown")
async def shutdown():
    await app.db_connection.close()


@app.get('/')
async def get_root():
    return {"message": "Hello World !"}


@app.get('/welcome')
async def welcome(request: Request, is_logged: bool = Depends(is_logged)):
    response = app.templates.TemplateResponse('welcome.html', {'request': request, 'user': app.user['login']})
    return response


@app.post('/login')
async def login(credentials: HTTPBasicCredentials = Depends(app.security)):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    correct_username = secrets.compare_digest(credentials.username, app.user['login'])
    correct_password = secrets.compare_digest(credentials.password, app.user['password'])

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    # session_token = sha256(str.encode(f"{credentials.username}:{app.secret_key}")).hexdigest()
    session_token = jwt.encode({app.API_KEY: True}, app.secret_key).decode("utf-8")

    response = RedirectResponse(url='/welcome', status_code=status.HTTP_302_FOUND)
    response.set_cookie(app.API_KEY, session_token)

    # session = {'user': credentials.username, 'token': session_token}
    # tokens.append(session)

    return response


@app.post('/logout')
async def logout(is_logged: bool = Depends(is_logged)):
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(app.API_KEY)
    return response


# Patients endpoints


@app.post('/patient')
async def add_patient(patient: PatientModel, is_logged: bool = Depends(is_logged)):
    # new_patient = PatientResponseModel(id=len(patients), patient=patient)
    # patients.append(new_patient)
    if len(app.patients.keys()) == 0:
        new_id = 0
    else:
        new_id = max(app.patients.keys()) + 1

    app.patients[new_id] = patient

    response = RedirectResponse(url=f'/patient/{new_id}', status_code=302)
    return response


@app.get('/patient')
async def get_patients(is_logged: bool = Depends(is_logged)):
    """Returns dict of patients as JSON"""
    return app.patients


@app.get('/patient/{pk}')
async def get_patient(pk: int, is_logged: bool = Depends(is_logged)):
    # patient_resp = next((patient for patient in patients if patient.id == pk), None)

    if pk in app.patients.keys():
        return app.patients[pk]
    else:
        return Response(status_code=204)


@app.delete('/patient/{pk}')
async def delete_patient(pk: int, is_logged: bool = Depends(is_logged)):
    if pk in app.patients.keys():
        del app.patients[pk]

    return Response(status_code=204)


# endpoints for chonnok db

@app.get('/tracks')
async def get_tracks(page: int = 0, per_page: int = 10):
    offset = page * per_page
    query = 'SELECT * FROM tracks ORDER BY trackid LIMIT ? OFFSET ? ;'
    app.db_connection.row_factory = aiosqlite.Row
    cursor = await app.db_connection.execute(query, (per_page, offset,))
    tracks = await cursor.fetchall()
    return tracks


@app.get("/tracks/composers")
async def get_tracks_composers(response: Response, composer_name: str):
    app.db_connection.row_factory = lambda row, x: x[0]
    cursor = await app.db_connection.execute("SELECT Name FROM tracks WHERE Composer = ? ORDER BY Name",
                                             (composer_name,))
    tracks = await cursor.fetchall()
    if len(tracks) == 0:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": {"error": "Sorry, there's no tracks of that composer."}}
    return tracks


@app.post("/albums")
async def add_album(response: Response, album: AlbumModel):
    app.db_connection.row_factory = None
    query = "SELECT ArtistId FROM artists WHERE ArtistId = ?"
    cursor = await app.db_connection.execute(query, (album.artist_id, ))
    result = await cursor.fetchone()
    if result is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": {"error": "Such artist does not exist in chinook database."}}
    cursor = await app.db_connection.execute("INSERT INTO albums (Title, ArtistId) VALUES (?, ?)",
                                                (album.title, album.artist_id, ))
    await app.db_connection.commit()
    response.status_code = status.HTTP_201_CREATED
    return {"AlbumId": cursor.lastrowid, "Title": album.title, "ArtistId": album.artist_id}


@app.get('/albums/{album_id}')
async def get_album_by_id(response: Response, album_id: int):
    app.db_connection.row_factory = aiosqlite.Row
    query = 'SELECT albumid, title, artistid FROM albums where albumid = ? ;'
    cursor = await app.db_connection.execute(query, (album_id, ))
    album = await cursor.fetchone()

    if album is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": {"error": "Sorry, there's no album with that ID."}}
    return album


@app.put('/customers/{customer_id}')
async def edit_customer(response: Response, new_customer: CustomerModel, customer_id: int):
    app.db_connection.row_factory = aiosqlite.Row

    query = 'SELECT customerid FROM customers WHERE customerid = ? ;'
    cursor = await app.db_connection.execute(query, (customer_id,))
    customer = await cursor.fetchone()


    if customer is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": {"error": "Sorry, there's no customer with that ID."}}

    update_customer = new_customer.dict(exclude_unset=True)

    query = 'UPDATE customers SET '
    for field in update_customer.keys():
        query += f'{field} = ? ,'
    query=query[:-1]
    query += 'WHERE customerid = ? ;'


    values = list(update_customer.values())
    values.append(customer_id)

    await app.db_connection.execute(query, tuple(values))
    await app.db_connection.commit()

    cursor = await app.db_connection.execute('SELECT * FROM customers WHERE customerid = ? ;', (customer_id,))
    customer = await cursor.fetchone()

    return customer


@app.get('/sales')
async def get_statistics(response: Response, category: str):
    app.db_connection.row_factory = aiosqlite.Row

    if category == "customers":
        app.db_connection.row_factory = aiosqlite.Row
        cursor = await app.db_connection.execute("""
        SELECT invoices.CustomerId, Email, Phone, ROUND(SUM(Total), 2) AS Sum
        FROM invoices JOIN customers on invoices.CustomerId = customers.CustomerId
        GROUP BY invoices.CustomerId ORDER BY Sum DESC, invoices.CustomerId
        """)
        stats = await cursor.fetchall()
        return stats
    elif category == "genres":
        app.db_connection.row_factory = aiosqlite.Row
        cursor = await app.db_connection.execute("""
        SELECT genres.Name, SUM(Quantity) AS Sum FROM invoice_items
        JOIN tracks ON invoice_items.TrackId = tracks.TrackId
        JOIN genres ON tracks.GenreId = genres.GenreId
        GROUP BY tracks.GenreId ORDER BY Sum DESC, genres.Name
        """)
        stats = await cursor.fetchall()
        return stats
    elif category == "media_types":
        app.db_connection.row_factory = aiosqlite.Row
        cursor = await app.db_connection.execute("""
        SELECT media_types.Name, SUM(Quantity) AS Sum FROM invoice_items
        JOIN tracks ON invoice_items.TrackId = tracks.TrackId
        JOIN media_types ON tracks.MediaTypeId = media_types.MediaTypeId
        GROUP BY tracks.MediaTypeId ORDER BY Sum DESC, media_types.Name
        """)
        stats = await cursor.fetchall()
        return stats
    elif category == "artists":
        app.db_connection.row_factory = aiosqlite.Row
        cursor = await app.db_connection.execute("""
        SELECT artists.Name, SUM(Quantity) AS Sum FROM invoice_items
        JOIN tracks ON invoice_items.TrackId = tracks.TrackId
        JOIN albums ON tracks.AlbumId = albums.AlbumId
        JOIN artists ON albums.ArtistId = artists.ArtistId
        GROUP BY albums.ArtistId ORDER BY Sum DESC, artists.Name
        """)
        stats = await cursor.fetchall()
        return stats
    elif category == "albums":
        app.db_connection.row_factory = aiosqlite.Row
        cursor = await app.db_connection.execute("""
        SELECT albums.Title, artists.Name as Artist, SUM(Quantity) AS Sum FROM invoice_items
        JOIN tracks ON invoice_items.TrackId = tracks.TrackId
        JOIN albums ON tracks.AlbumId = albums.AlbumId
        JOIN artists ON albums.ArtistId = artists.ArtistId
        GROUP BY tracks.AlbumId ORDER BY Sum DESC, albums.Title
        """)
        stats = await cursor.fetchall()
        return stats
    elif category == "tracks":
        app.db_connection.row_factory = aiosqlite.Row
        cursor = await app.db_connection.execute("""
         SELECT tracks.Name, albums.Title as AlbumTitle, artists.Name as Artist, SUM(Quantity) AS Sum FROM invoice_items
         JOIN tracks ON invoice_items.TrackId = tracks.TrackId
         JOIN albums ON tracks.AlbumId = albums.AlbumId
         JOIN artists ON albums.ArtistId = artists.ArtistId
         GROUP BY invoice_items.TrackId ORDER BY Sum DESC, tracks.Name
         """)
        stats = await cursor.fetchall()
        return stats
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"detail": {"error": "No such category."}}