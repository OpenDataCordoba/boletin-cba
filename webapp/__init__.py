import os
import mistune
import datetime
import sqlalchemy as sa
from flask import Flask, render_template, abort, Markup
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Column, String, Integer, Date, Text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///boletin')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

markdown = mistune.Markdown()


class SeccionBoletin(db.Model):
    __tablename__ = 'seccion_boletin'

    titulo = Column(String(1000), primary_key=True)
    slug = Column(Text)
    date = Column(Date, primary_key=True)
    url = Column(Text)
    file_path = Column(Text)
    content = Column(Text)

    def __repr__(self):
        return "<SeccionBoletin: titulo='%s', date='%s'>" % (self.titulo, self.date)


@app.route("/about/")
def about():
    return render_template('about.html')


@app.route("/")
def home():
    query = db.session.query(sa.distinct(sa.cast(sa.func.extract('year', SeccionBoletin.date), sa.Integer)).label('year'))
    query = query.order_by('year')
    return render_template('home.html', years=query)


@app.route("/<int:year>/")
def year(year):
    distinct_month = sa.distinct(sa.cast(sa.func.extract('month', SeccionBoletin.date), sa.Integer)).label('month')
    query = db.session.query(distinct_month)
    query = query.filter(sa.func.extract('year', SeccionBoletin.date) == year)
    query = query.order_by('month')

    return render_template('year.html', year=year, months=query)


@app.route("/<int:year>/<int:month>/")
def month(year, month):
    distinct_day = sa.distinct(sa.cast(sa.func.extract('day', SeccionBoletin.date), sa.Integer)).label('day')
    query = db.session.query(distinct_day)
    query = query.filter(sa.func.extract('year', SeccionBoletin.date) == year)
    query = query.filter(sa.func.extract('month', SeccionBoletin.date) == month)
    query = query.order_by('day')
    return render_template('month.html', year=year, month=month, days=query)


@app.route("/<int:year>/<int:month>/<int:day>/")
def day(year, month, day):
    date = datetime.date(year, month, day)
    secciones = db.session.query(SeccionBoletin).filter(SeccionBoletin.date == date)
    return render_template('day.html', year=year, month=month, day=day, secciones=secciones)


@app.route("/<int:year>/<int:month>/<int:day>/<slug>/")
def seccion(year, month, day, slug):
    date = datetime.date(year, month, day)
    seccion = db.session.query(SeccionBoletin).filter(
        SeccionBoletin.date == date,
        SeccionBoletin.slug == slug
    ).first()
    if not seccion:
        abort(404)
    # content = Markup(markdown(seccion.content))
    content = seccion.content
    return render_template('seccion.html', year=year, month=month, day=day, seccion=seccion, content=content)


if __name__ == "__main__":
    app.run()