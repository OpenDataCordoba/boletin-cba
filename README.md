# Scrapper de los Boletines Oficiales de la Provincia de Cordoba

Scrapper para descargar todos los boletines oficiales de la página del [Gobierno de la Provincia de Córdoba](http://boletinoficial.cba.gov.ar).

Requiere:
* progressbar2
* PyPDF2
* jnius para usar Tika

Para utilizar Tika como extractor de texto del PDF ver el siguiente link (requiere la descarga de libreria):
* [http://www.hackzine.org/using-apache-tika-from-python-with-jnius.html](http://www.hackzine.org/using-apache-tika-from-python-with-jnius.html)


# Scraper

```
$ cd boescraper
$ scrapy crawl boe -o boletines.jl
```