from fastapi import APIRouter, Depends, HTTPException
from models.user import Symbols, User
from auth.user import AuthHandler
from database.user import add_user, add_symbols, get_symbols, get_prices, get_stocks_csv, get_users
from datetime import date, timedelta


routes_user = APIRouter()
auth_handler = AuthHandler()


today = date.today()
yesterday = today - timedelta(days=1)


@routes_user.get("/")
def home():
    return{ "message": "Welcome to the ultimate stocks API!" }


# Registrar usuario
@routes_user.post("/register", status_code=201)
def register(user: User):
    """
    Registrar con un body del tipo:
    {
        'username': 'miguel_el_humilde',
        'password': 'clavesecreta'
    }
    """
    # Siempre se debe guardar el hash de la clave, no la clave en texto plano
    hashed_password = auth_handler.get_password_hash(user.password)
    return add_user( {"username": user.username, "password": hashed_password} )


# Hacer login con usuario y clave registrados
@routes_user.post('/login')
def login(user: User):
    """
    Iniciar sesión con el usuario y clave previamente registrados
    {
        'username': 'miguel_el_humilde',
        'password': 'clavesecreta'
    }
    """
    users_db = get_users()
    user_tmp = None
    for x in users_db:
        if x['username'] == user.username:
            user_tmp = x
            break
    
    if (user_tmp is None) or (not auth_handler.verify_password(user.password, user_tmp['password'])):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(user_tmp['username'])
    return { 'token': token }


# User story 1
@routes_user.get("/get/symbols")
def get_all_symbols(username=Depends(auth_handler.auth_wrapper)):
    return get_symbols()


# User story 2
@routes_user.post("/save/symbols", response_model=Symbols)
def add(symbols: Symbols, username=Depends(auth_handler.auth_wrapper)):
    return add_symbols(symbols.dict(), username)


# User story 3
@routes_user.get("/get/prices/{symbol}") # Ruta con query parameters
def get_prices_by_symbol(symbol: str, start: str=yesterday, end: str=today, interval: str="60m", username=Depends(auth_handler.auth_wrapper)):
    """
    Ejemplo de llamado de la ruta: 'http://.../get/prices/AAPL?start=2022-03-23&end=2022-03-27&interval=30m'
    """
    return get_prices(symbol, start, end, interval, username)


# User story 4
@routes_user.get("/get/csv")
async def get_csv(username=Depends(auth_handler.auth_wrapper)):
    return get_stocks_csv(username)
