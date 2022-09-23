from .db import dynamodb
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Attr
from fastapi.responses import JSONResponse, StreamingResponse
from datetime import date, timedelta

import pandas as pd
import numpy as np
import yfinance as yf
import io

stocks_table = dynamodb.Table("stocks_prices")
user_preferences_table = dynamodb.Table("user_preferences")
users_table = dynamodb.Table("users")


today = date.today()
yesterday = today - timedelta(days=1)


# Añade un usuario a la BD
def add_user(user: dict):
    """
    user: (nuevo usuario registrado) (p.ej) { "username": "lord_miguel", "password": "algún_hash"}
    """
    print("xdxd", user)
    try:
        users_table.put_item(Item=user, ConditionExpression=Attr("username").ne(user["username"])) # Que el usuario no exista ya
        return user
    except ClientError as e:
        return JSONResponse(content=e.response["Error"], status_code=500)


# Revisa que el usuario exista en la BD
def check_user(user: dict):
    """
    user: (usuario a evaluar) (p.ej) { "username": "lord_miguel", "password": "algún_hash"}
    """
    try:
        users_table.get_item(hash_key=user["username"]) # Que el usuario no exista ya
        return True
    except ClientError as e:
        return JSONResponse(content=e.response["Error"], status_code=500)


# Retorna todos los usuarios en la BD
def get_users():
    response = users_table.scan()
    result = response["Items"]
    while "LastEvaluatedKey" in response:
        response = stocks_table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        result.extend(response["Items"])
    return result


# Retorna todos los símbolos disponibles 
def get_symbols():
    stocks = pd.read_html("https://finance.yahoo.com/trending-tickers")[0]
    tickers = np.array(stocks["Symbol"])
    return { "symbols": list(tickers) }


# Añade los símbolos de interés para el usuario a la BD
def add_symbols(symbols: dict, username):
    """
    symbols: (símbolos de interés para el usuario) (p.ej) { 'symbols': ['AAPL', 'MSFT', 'NFLX'] }
    username: (usuario logueado) (p.ej) 'miguelvalzul'
    """
    try:
        symbols_bd = symbols.copy()
        symbols_bd["user_id"] = username
        user_preferences_table.put_item(Item=symbols_bd)
        return symbols_bd
    except ClientError as e:
        return JSONResponse(content=e.response["Error"], status_code=500)


# Añade un stock a la BD
def add_stock(stock: dict):
    """
    stock: (precios de un stock en cierta fecha para x usuario) (p.ej) 
    { 
    'user_id': 'user1', 
    'date': '2022-01-01', 
    'symbol': 'NFLX', 
    'high': '124.332', 
    'open': '110.99', 
    'low': '109. 0', 
    'close': '123.22'
    }
    """
    try:
        stocks_table.put_item(Item=stock)
        return stock
    except ClientError as e:
        return JSONResponse(content=e.response["Error"], status_code=500)


# Retorna los precios HOLC para un stock en específico en un rango de tiempo (por defecto retorna de ayer hasta hoy, con un intervalo de 1 hora)
def get_prices(symbol, start, end, interval, username):
    """
    symbol: (símbolo de la empresa en el mercado de valores) (p.ej) 'AAPL'
    start:  (fecha inicial) (p.ej) '2022-01-01'
    end:   (fecha final)     (p.ej) '2022-02-01
    interval: (periodicidad de los resultados) (p.ej) '30m'
    username: (usuario logueado) (p.ej) 'miguelvalzul'
    """
    ticker = yf.Ticker(symbol)
    stock_history = ticker.history(start=start, end=end, interval=interval) 
    dates = np.array(stock_history.index)
    
    stock_values = stock_history.values.tolist()
    prices = list(map(lambda x:x[:4], stock_values))
  
    # Añade los stocks a la BD
    for idx, stock in enumerate(stock_values):
        add_stock({
            "user_id": username,
            "date": str(dates[idx]),
            "symbol": symbol,
            "high": str(stock[0]),
            "open": str(stock[1]),
            "low": str(stock[2]),
            "close": str(stock[3])
        })
    return { f"OHLC prices for {symbol} from {start} to {end}": prices }


def get_stocks_csv(username):
    response = stocks_table.scan()
    result = response["Items"]

    while "LastEvaluatedKey" in response:
        response = stocks_table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        result.extend(response["Items"]) 

    data = pd.DataFrame(result)
    filtered_data = data[data["user_id"] == username]
    filtered_data = filtered_data[["date","symbol","high","open","low","close"]] # Reordena las columnas para mejor legibilidad
    
    stream = io.StringIO()
    filtered_data.to_csv(stream, index=False)
    stream_response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    stream_response.headers["Content-Disposition"] = "attachment; filename=all_stocks.csv"
    return stream_response

