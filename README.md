# Scrapper de los Boletines Oficiales de la Provincia de Cordoba

Scrapper para descargar todos los boletines oficiales de
la página del [Gobierno de la Provincia de Córdoba](http://boletinoficial.cba.gov.ar).


## Scraper
Crear una base de datos llamada `boletin`. Iniciar schema con 
```
$ ./main.py init_db
```
y luego correr el scraper con

```
$ scrapy crawl boe
```

## Website

Correr con
```
$ FLASK_APP=app.py flask run
```

## Build

Para construir el sitio estático, correr
```
$ python app.py
```
con lo que el sitio será construido en `webapp/build`


## Deploy

Con las credenciales de aws en algún lugar accesible a boto3, correr:
```
$ s3-deploy-website
```

## Heroku

```
$ heroku apps:create boletin-cba
$ heroku addons:create heroku-postgresql:hobby-dev -a boletin-cba
```
