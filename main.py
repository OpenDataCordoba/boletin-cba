#!/usr/bin/env python3

"""
Created on Tue Feb  2 18:01:54 2016

@author: pdelboca

References:
===========
 - PyPDF2: https://github.com/mstamy2/PyPDF2
 - Tika: http://www.hackzine.org/using-apache-tika-from-python-with-jnius.html
"""
import os.path
from PyPDF2 import PdfFileReader, utils
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import re
import subprocess
import mimetypes
import progressbar
import csv
import os
import re
import click
import boto3


_DATA_PATH = os.path.join(os.path.realpath(os.path.dirname(__file__)), "data")
_TXT_BOLETINES_PATH = os.path.join(_DATA_PATH, "urls_boletin.txt")
_PDF_PATH = os.path.join(_DATA_PATH, "pdfs")
_TXT_PATH = os.path.join(_DATA_PATH, "txts")
_BUCKET_NAME = 'boletin-cba'


@click.group()
def cli():
    pass


def walk_dir(base_dir):
    for root, _, files in os.walk(base_dir):
        rel_dir = os.path.relpath(root, base_dir)
        for file in files:
            yield os.path.join(rel_dir, file)


@cli.command()
def deploy():
    """Enviar el contenido del la carpeta data a s3"""
    client = boto3.client('s3')
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(_BUCKET_NAME)

    for file_path in walk_dir(_DATA_PATH):
        key = file_path.replace('./', '')
        try:
            client.head_object(Bucket=_BUCKET_NAME, Key=key)
            click.echo(key + ' found, skiping...')
        except Exception as e:
            click.echo('Subiendo ' + file_path)
            mime, _ = mimetypes.guess_type(file_path)
            bucket.upload_file(
                os.path.join(_DATA_PATH, file_path),
                key,
                ExtraArgs={'ACL': 'public-read',
                'ContentType': mime}
            )


@cli.command()
def scrapear():
    """
    Scrapea iterativamente todos los links a los pdfs de los boletines de
    la pagina:
        - http://boletinoficial.cba.gov.ar/{year}/{month}/
    Nota:
        - El metodo junta todos los links y los exporta a un txt para luego ser
        usados. Esto no es necesario, pero queria tener una lista de links
        para compartir.
        - Scrapea los links a los pdf encontrados en la página, en la práctica
        son solo boletines oficiales. Pero la logica no hace chequeo alguno de
        que realmente sean. Si hay otros archivos en pdf, tambien los descarga.
    """
    pdf_links = []
    for year in range(2007, 2018):
        click.echo("Scrapeando links del {0}".format(year))
        for month in range(1, 13):
            url = "http://boletinoficial.cba.gov.ar/{0}/{1}/".format(year, str(month).zfill(2))
            req = Request(url)
            try:
                response = urlopen(req)
            except HTTPError as e:
                click.echo('Error en la url: {0}'.format(url))
            except URLError as e:
                click.echo('Error en la url: {0}'.format(url))
            else:
                html = response.read()
                links = re.findall('"(http:\/\/.*?)"', str(html))
                pdf_links.extend([link for link in links if link.endswith('.pdf')])
    click.echo("Links obtenidos, comenzando la escritura a archivo...")
    with open(_TXT_BOLETINES_PATH, "w") as urls_file:
        for link in pdf_links:
            urls_file.write("%s\n" % link)
    click.echo("Escritura finalizada.")


@cli.command()
def descargar():
    """
    Descarga iterativamente todos los pdf de la pagina:
        - http://boletinoficial.cba.gov.ar/{year}/{month}/
    Nota:
        - Utiliza los links obtenidos en el método scrapear_url_boletines
    """
    os.makedirs(_PDF_PATH, exist_ok=True)
    if not os.path.isfile(_TXT_BOLETINES_PATH):
        click.echo("No existe el archivo: {0}".format(_TXT_BOLETINES_PATH))
        click.echo("Ejecute el metodo scrapear_url_boletines para obtener las url.")
        return

    click.echo("Comenzando la descarga de Boletines")
    urls = []
    with open(_TXT_BOLETINES_PATH, 'r') as url_boletines:
        urls = url_boletines.read().splitlines()

    with click.progressbar(urls) as bar:
        for url in bar:
            parsed = urlparse(url)
            filename = '/'.join(parsed.path.split('/')[-3:])
            file_path = os.path.join(_PDF_PATH, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            if os.path.isfile(file_path):
                click.echo('Salteando\n' + file_path)
                continue

            req = Request(url)
            try:
                pdf_file = urlopen(req)
            except HTTPError as e:
                click.echo('Error en la url: {0}'.format(url))
                click.echo(e.code, " - ", e.reason)
            except URLError as e:
                click.echo('Error en la url: {0}'.format(url))
                click.echo(e.code, " - ", e.reason)
            else:
                with open(file_path, 'wb') as local_file:
                    local_file.write(pdf_file.read())
    click.echo("Descarga Finalizada")


@cli.command()
def pdf_to_txt():
    """
    Iterates throught all the pdf stored in ./data/pdf/ folder and export its
    content to a txt file.
    It uses the pdftotxt command from linux.
    """
    os.makedirs(_TXT_PATH, exist_ok=True)
    for fn in walk_dir(_PDF_PATH):
        file_path = os.path.join(_PDF_PATH, fn)

        if not file_path.endswith(".pdf"):
            continue
        try:
            txt_name = fn.replace('.pdf', '.txt')
            txt_path = os.path.join(_TXT_PATH, txt_name)
            print(file_path)
            subprocess.run(["pdftotext", "--raw", file_path, txt_path])
        except utils.PdfReadError as e:
            click.echo("Error al leer el PDF: {0}".format(fn))
        except Exception as e:
            click.echo("Error desconocido en el PDF: {0}".format(fn))
            click.echo("Error: {0}".format(e))


@cli.command()
def limpiar_texto(text):
    """
    Funcion para limpiar los execivos end of lines que vienen tras la extraccion
    del texto en pdf.
    """
    # TODO: Use NLTK's sentence segmentation.
    new_text = ""
    for line in text.split('\n'):
        if len(line) > 0:
            new_text += line + " "
        else:
            new_text += '\n'
    return new_text


if __name__ == "__main__":
    cli()
