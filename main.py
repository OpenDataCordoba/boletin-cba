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
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import re
import progressbar
import csv
import os
import re
import click
os.environ['CLASSPATH'] = "./lib/tika-app-1.11.jar"
#from jnius import autoclass

_DATA_PATH = os.path.join(os.path.realpath(os.path.dirname(__file__)), "data")
_PDF_PATH = os.path.join(_DATA_PATH, "pdfs")
_TXT_BOLETINES_PATH = os.path.join(_DATA_PATH, "urls_boletin.txt")


@click.group()
def cli():
    pass


@cli.command()
def scrapear_url_boletines():
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
    click.echo('test')
    pdf_links = []
    for year in range(2007, 2018):
        print("Scrapeando links del {0}".format(year))
        for month in range(1, 13):
            url = "http://boletinoficial.cba.gov.ar/{0}/{1}/".format(year, str(month).zfill(2))
            req = Request(url)
            try:
                response = urlopen(req)
            except HTTPError as e:
                print('Error en la url: {0}'.format(url))
                print(e.code, " - ", e.reason)
            except URLError as e:
                print('Error en la url: {0}'.format(url))
                print(e.code, " - ", e.reason)
            else:
                html = response.read()
                links = re.findall('"(http:\/\/.*?)"', str(html))
                pdf_links.extend([link for link in links if link.endswith('.pdf')])
    print("Links obtenidos, comenzando la escritura a archivo...")
    with open(_TXT_BOLETINES_PATH, "w") as urls_file:
        for link in pdf_links:
            urls_file.write("%s\n" % link)
    print("Escritura finalizada.")


@cli.command()
def descargar_boletines():
    """
    Descarga iterativamente todos los pdf de la pagina:
        - http://boletinoficial.cba.gov.ar/{year}/{month}/
    Nota:
        - Utiliza los links obtenidos en el método scrapear_url_boletines
    """
    os.makedirs(_PDF_PATH, exist_ok=True)
    if not os.path.isfile(_TXT_BOLETINES_PATH):
        print("No existe el archivo: {0}".format(_TXT_BOLETINES_PATH))
        print("Ejecute el metodo scrapear_url_boletines para obtener las url.")
    else:
        print("Comenzando la descarga de Boletines")
        with open(_TXT_BOLETINES_PATH, 'r') as url_boletines:
            urls = url_boletines.read().splitlines()
        bar = progressbar.ProgressBar()
        for url in bar(urls):
            filename = url.split("/")[-1]
            file_path = os.path.join(_PDF_PATH, filename)
            req = Request(url)
            try:
                pdf_file = urlopen(req)
            except HTTPError as e:
                print('Error en la url: {0}'.format(url))
                print(e.code, " - ", e.reason)
            except URLError as e:
                print('Error en la url: {0}'.format(url))
                print(e.code, " - ", e.reason)
            else:
                with open(file_path, 'wb') as local_file:
                    local_file.write(pdf_file.read())
    print("Descarga Finalizada")


@cli.command()
def pdf_to_csv():
    """
    Iterates throught all the pdf stored in ./data/pdf/ folder and export its
    content to the file data.csv.
    The format of the csv file should have two columns: id and text
    """
    bar = progressbar.ProgressBar()
    csv_data_file = os.path.join(_DATA_PATH, "data_tika.csv")
    Tika = autoclass('org.apache.tika.Tika')
    Metadata = autoclass('org.apache.tika.metadata.Metadata')
    FileInputStream = autoclass('java.io.FileInputStream')
    tika = Tika()
    meta = Metadata()
    with open(csv_data_file, "w", newline='') as csvfile:
        data_writer = csv.writer(csvfile)
        data_writer.writerow(["document_id", "document_text"])
        for fn in bar(os.listdir(_PDF_PATH)):
            filename = os.path.join(_PDF_PATH, fn)
            if filename.endswith(".pdf"):
                try:
                    text = tika.parseToString(FileInputStream(filename), meta)
                except Exception as e:
                    print("Error desconocido en el PDF: {0}".format(fn))
                    print("Error: {0}".format(e))
                else:
                    #TODO: Check if text is not empty
                    text = limpiar_texto(text)
                    data_writer.writerow([fn,text])


@cli.command()
def pdf_to_csv_with_PyPDF():
    """
    Iterates throught all the pdf stored in ./data/pdf/ folder and export its
    content to the file data.csv.
    The format of the csv file should have two columns: id and text
    """
    bar = progressbar.ProgressBar()
    csv_data_file = os.path.join(_DATA_PATH, "data.csv")
    with open(csv_data_file, "w", newline='') as csvfile:
        data_writer = csv.writer(csvfile)
        data_writer.writerow(["document_id","document_text"])
        for fn in bar(os.listdir(_PDF_PATH)):
            file_path = os.path.join(_PDF_PATH, fn)
            if file_path.endswith(".pdf"):
                try:
                    input_file = PdfFileReader(open(file_path, 'rb'))
                    text = ""
                    for p in range(input_file.getNumPages()):
                        text += input_file.getPage(p).extractText() + " "
                except utils.PdfReadError as e:
                    print("Error al leer el PDF: {0}".format(fn))
                except Exception as e:
                    print("Error desconocido en el PDF: {0}".format(fn))
                    print("Error: {0}".format(e))
                else:
                    #TODO: Check if text is not empty
                    data_writer.writerow([fn, text.encode("utf-8")])


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
