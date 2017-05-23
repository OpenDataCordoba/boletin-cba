web: gunicorn app:app -R --error-logfile=- --access-logfile=- --reload
scrape: scrapy crawl boe
dbupgrade: FLASK_APP=app.py flask db upgrade
