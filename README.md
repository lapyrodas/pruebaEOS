# pruebaEOS

Prueba EOS para optar al proyecto fortalecimiento de la actividad pesquera

## Tabla de contenido

- [Tecnologias](#tecnologias)
- [Instalacion](#instalacion)
- [API](#api)

## Tecnologias

Esta API-REST fue construida con:

- Flask==2.0.3
- Flask-RESTful==0.3.9

* requests==2.27.1

Solicitudes USGS:

- https://m2m.cr.usgs.gov/api/api/json/stable

## Instalacion

1. Clone el repositorio en una ubicación conocidad.
   USER_USGS = "lapyemperor"
2. En el archivo _.env_ configure (**USER_USGS**,**USER_PASS**)con el usuario y la contraseña para acceder al API https://m2m.cr.usgs.gov/ (sin estas credenciales no podrá usar el API-REST local)
3. Debe tener instalado docker y docker-compose en su equipo y poder acceder a sus funciones desde la terminal.
4. Abra desde la terminal la carpeta EOS y ejecute el siguiente comando:

```
$ docker-compose up
```

Ahora podrá acceder la API-REST mediante el localhost de su maquina en el puerto 5000 al puerto 5000 del container donde se está ejecutando el API.

## API

### Raiz

http://127.0.0.1:5000/pruebaeos

Solicitudes permitidas

### Listar imagenes de una colección

- http://127.0.0.1:5000/pruebaeos/catalogo

```
{
    "dataset":"landsat_8_c1",
    "lat":"1.45",
    "lon":"-78.6298",
    "fecha_inicio":"2018-01-01",
    "fecha_fin":"2019-01-01",
    "nubosidad_max":"80"
}
```

- dataset: corresponde al alias de la colección
- lat: Latitud del punto de interes, esto debe estar en coordenadas geograficas.

* lon: Longitud del punto de interes,esto debe estar en coordenadas geograficas.
* fecha_inicio: filtro de fecha desde donde se desea realizar la busqueda.
* fecha_fin: filtro de fecha hasta donde se desea realiza la busqueda.

**Response**

```
{
    "escenas_encontradas": 14,
    "escenas": [
        {
            "fecha": "2018-12-28",
            "identificador": "LC08_L1TP_010059_20181228_20190129_01_T1",
            "entityId": "LC80100592018362LGN00"
        },
    ]
}
```

### Manipulacion GEOTIFF

http://127.0.0.1:5000/pruebaeos/descarga

- #### Descargar

```
{
    "dataset":"landsat_8_c1",
    "escena":"LC80100592018362LGN00",
    "out_dir": "./temporal",
    "accion":"descarga"
}
```

**Response**

```
{
    "escena":"LC08_L1TP_010059_20181228_20190129_01_T1",
    "url": "http://localhost:5000/pruebaeos/temporal/LC08_L1TP_010059_20181228_20190129_01_T1"
}

```

- #### Listar contenido

```
{
    "dataset":"landsat_8_c1",
    "escena":"LC80100592018362LGN00",
    "out_dir": "./temporal",
    "accion":"listar"
}
```

**Response**

```
{
    "escena": "LC08_L1TP_010059_20181228_20190129_01_T1",
    "url": "http://1010010056:5000/pruebaeos/temporal/LC08_L1TP_010059_20181228_20190129_01_T1",
    "archivos": [
        {
            "bandas1": "LC08_L1TP_010059_20181228_20190129_01_T1_B1.TIF",
            "bandas10": "LC08_L1TP_010059_20181228_20190129_01_T1_B10.TIF",
            "bandas11": "LC08_L1TP_010059_20181228_20190129_01_T1_B11.TIF",
            "bandas2": "LC08_L1TP_010059_20181228_20190129_01_T1_B2.TIF",
            "bandas3": "LC08_L1TP_010059_20181228_20190129_01_T1_B3.TIF",
            "bandas4": "LC08_L1TP_010059_20181228_20190129_01_T1_B4.TIF",
            "bandas5": "LC08_L1TP_010059_20181228_20190129_01_T1_B5.TIF",
            "bandas6": "LC08_L1TP_010059_20181228_20190129_01_T1_B6.TIF",
            "bandas7": "LC08_L1TP_010059_20181228_20190129_01_T1_B7.TIF",
            "bandas8": "LC08_L1TP_010059_20181228_20190129_01_T1_B8.TIF",
            "bandas9": "LC08_L1TP_010059_20181228_20190129_01_T1_B9.TIF"
        }
    ]
}
```

Ó

```
{
    "escena": "LC08_L1TP_010059_20181228_20190129_01_T",
    "mensaje": "Escena no encontrada"
}
```

- dataset: corresponde al alias de la colección
- escena: corresponde al entityID de la imagen que se desea descargar (usar [lista de imagenes](#listar-imagenes-de-una-colecci%C3%B3n) para obtener el ID)
- out_dir: Nombre de la carpeta donde se va descargar la imagen
- ### Accion:
  - **_descarga_** : Descarga la escena en la carpeta indicada.
  * **_listar_**: Lista el contenido de la Escena Indicada.

El producto a descargar es **"Level-1 GeoTIFF Data Product"**
