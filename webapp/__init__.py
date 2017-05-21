from datetime import datetime
import sqlalchemy as sa
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Date, Text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///boletin'
db = SQLAlchemy(app)


class SeccionBoletin(db.Model):
    __tablename__ = 'seccion_boletin'

    titulo = Column(String(1000), primary_key=True)
    date = Column(Date, primary_key=True)
    url = Column(Text)
    file_path = Column(Text)
    content = Column(Text)

    def __repr__(self):
        return "<SeccionBoletin: titulo='%s', date='%s'>" % (self.titulo, self.date)


def query_date_part(part):
    return db.session.query(sa.distinct(sa.cast(sa.func.extract(part, SeccionBoletin.date), sa.Integer)).label(part))


@app.route("/")
def home():
    years = query_date_part('year')
    return render_template('home.html', years=years)


@app.route("/<int:year>/")
def year(year):
    months = query_date_part('month')
    return render_template('year.html', year=year, months=months)


@app.route("/<int:year>/<int:month>/")
def month(year, month):
    days = query_date_part('day')
    return render_template('month.html', year=year, month=month, days=days)


@app.route("/<int:year>/<int:month>/<int:day>/")
def day(year, month, day):
    secciones = db.session.query(SeccionBoletin).filter(SeccionBoletin.date == '2017-05-19')
    return render_template('day.html', year=year, month=month, day=day, secciones=secciones)


if __name__ == "__main__":
    app.run()