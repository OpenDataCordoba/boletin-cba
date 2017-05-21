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


@app.route("/")
def home():
    secciones = db.session.query(SeccionBoletin)
    years = db.session.query(sa.distinct(sa.func.date_part('YEAR', SeccionBoletin.date))).all()
    return render_template('home.html', years=years)


@app.route("/<int:year>")
def year(year):
    months = ['1','2']
    return render_template('year.html', year=year, months=months)


if __name__ == "__main__":
    app.run()