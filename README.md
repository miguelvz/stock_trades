# API para estar al tanto de los precios de las acciones en el mercado de valores

Esta es una guía para desplegar la API y consumirla localmente. La implementación requiere python 3.10.+ y una llave de acceso de su cuenta AWS.

# Instalación

1. Clone el repositorio público del proyecto por medio del comando 

    `git clone https://github.com/miguelvz/stock_trades.git`

2. Se recomienda crear un entorno virtual. Para esto, en Windows, desde la terminal ejecute el comando
    
    `py -3 -m venv venv`

    y en macOS/Linux:

    `python3 -m venv venv`

3. Active el entorno, en Windows, mediante el comando 
    
    `venv\Scripts\activate`

    y en macOS/Linux:

    `. venv/bin/activate`

    En este punto ya debería ver `(venv)` en la parte izquierda de la terminal, indicando que el entorno se encuentra activo, como puede ver en la siguiente imagen
    
    ![image info](./imgs/active.PNG)

4. En el repositorio puede encontrar el archivo `requirements.txt` que contiene las dependencias necesarias para ejecutar el proyecto. Instálelas mediante el comando
    
    `pip install requirements.txt`

5. Cree un archivo `.env` dentro de la carpeta del repositorio, al nivel de las carpetas `auth`, `database`, etc. Es decir, la ruta del archivo debería quedar algo como
   `D:\Users\Pepito\Documents\stock_trades\.env`

   Este archivo va a contener las llaves de acceso de AWS para poder usar el servicio de bases de datos de `DynamoDB`. Si no tiene una llave, puede crear una fácilmente desde la consola de AWS una vez logueado haciendo click en su usuario -> Credenciales de seguridad -> Claves de acceso -> Crear una clave de acceso
   Con esto ya puede crear las 3 variables necesarias en el archivo `.env`. Este debería verse algo como

   `AWS_ACCESS_KEY_ID=AKIA6QVGQ4LK6F65CXPJSSB`

   `AWS_SECRET_ACCESS_KEY=od5eazAXlxYnup4R5fJGIVpds6E1q96x+DfTHmCa`

   `REGION_NAME=us-east-1`

6. Ya con esto se puede ejecutar localmente la aplicación mediante el comando

   `uvicorn main:app --reload --env-file=".env"`

   Tenga en cuenta que tiene que ejecutar ese comando dentro de la carpeta del repositorio, al nivel de los archivos `main.py` y `.env`

   Ahí nos debería salir un mensaje en la terminal diciendo que la API ya está disponible por la ruta `127.0.0.1:8000`, como puede ver a continuación:
 
   ![image info](./imgs/success.PNG)

    Si navega a esa ruta en el navegador, debería ver un pequeño mensaje de bienvenida a la API, como puede ver en la siguiente imagen

    ![image info](./imgs/welcome.PNG)

    Con esto culmina la guía de instalación, y seguimos explicando cada una de las rutas.

# Rutas REST API

Todas las rutas reciben y retornan resultados en formato JSON.

## Rutas de autenticación

La API maneja un sistema de autenticación sencillo con tokens JWT para evitar accesos/cambios no deseados

- `/register`: Petición por el método **POST** que recibe usuario y contraseña y retorna estos mismos en caso de éxito, o mensaje de error en caso de que el usuario ya exista en la base de datos. Ejemplo:

```
localhost:8000/register

Ingresa usuario y contraseña

{
    "username": "miguelelhumilde",
    "password": "superclave"
}
```

- `/login`: Petición por el método **POST** que verifica usuario y contraseña para iniciar sesión y retorna el token, que expira en 1 hora, requerido para acceder a la funcionalidad de las demás rutas. Ejemplo:

```
localhost:8000/login

Ingresa usuario y contraseña

{
    "username": "miguelelhumilde",
    "password": "superclave"
}

Retorna el respectivo token

{
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NjM5NTM5MzgsImlhdCI6MTY2Mzk1MDMzOCwic3ViIjoibWlndWVsdmFsenVsMTIzIn0.55U0moUFqc7v49hxGEIS6esTNYTBTZ6oMgpJ8lYzdIc"
}
```

## Verificaciones para acceder a rutas

En adelante todas las rutas requieren el token generado al iniciar sesión por la ruta `/login`. Este token debe ser incluido en el header de las peticiones como el atributo `Authorization` y como valor la palabra **Bearer** seguida del token. Ejemplo: `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2NjM5NTM5Mz`


## Rutas de los stocks

- `/get/symbols`: Petición por el método **GET** que retorna todos los símboles disponibles para ser usados. Ejemplo: 
```
localhost:8000/get/symbols

Retorna la lista de símbolos

{
    "symbols": [
        "CL=F",
        "COST",
        "GBPUSD=X",
        "TELL",
        "LITM",
        "ATHX",
        "^DJI",
        "MULN",
        "DPZ",
        "CANO",
        "^GSPC",
        "FDX",
        "META",
        "SU.TO",
        "XOM",
        "ATXI",
        "DVN",
        "CVX",
        "OXY",
        "FUBO",
        "CS",
        "SONX",
        "GOLD",
        "KRBP",
        "CO",
        "XLE",
        "EURUSD=X",
        "F",
        "GC=F",
        "ENB.TO"
    ]
}

```

- `save/symbols`: Petición por el método **POST** para guardar los símbolos de interés para el usuario y poder ver sus precios más tarde. Ejemplo:

```
localhost:8000/save/symbols

Ingresa lista de símbolos a guardar

{
    "symbols": ["AAPL", "NFLX", "TSLA", "MSFT"]
}

Retorna los símbolos, el usuario que los guardó y la hora a la que los guardó

{
    "user_id": "miguelvalzul123",
    "symbols": [
        "AAPL",
        "NFLX",
        "TSLA"
        "MSFT",
    ],
    "created_at": "2022-09-23 11:26:29.981978"
}
```

- `get/prices/:symbol`: Petición por el método **GET** que retorna los precios OHLC (open, high, low y close) para una acción en específico en un intervalo de tiempo dado. La ruta recibe tres parámetros: `start`, `end` e `interval`. Si no se colocan estos, por defecto se devuelven los precios entre ayer y hoy, con un intervalo de 60 minutos entre precios. Ejemplo:
```
localhost:8000/get/prices/AAPL?start=2022-01-01&end=2022-01-04&interval=90m

Retorna los precios en este rango de tiempo

{
    "OHLC prices for AAPL from 2022-01-01 to 2022-01-04": [
        [
            335.3500061035156,
            337.42999267578125,
            329.7799987792969,
            332.54998779296875
        ],
        [
            332.5450134277344,
            332.5899963378906,
            331.08929443359375,
            331.989990234375
        ],
        [
            331.989990234375,
            332.9599914550781,
            331.30999755859375,
            332.6400146484375
        ]
        ...
}
```

- `get/csv`: Petición por el método **GET** que retorna un CSV con todos los stocks que guardó el usuario en el pasado. Cada usuario puede ver únicamente los stocks que él mismo haya consultado antes. Si se ingresa el token en la cabecera del navegador, la descarga del archivo se hace automática y se guarda como `all_stocks.csv`. La otra opción, un poco más sencilla, es hacer la petición por Postman y darle a descargar ahí. Ejemplo:

```
localhost:8000/get/csv

Retorna archivo all_stocks.csv con la información de fecha, símbolo y precios OHLC para cada stock
```




