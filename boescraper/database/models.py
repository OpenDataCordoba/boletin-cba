from sqlalchemy import Column, String, Integer, Date, Text
from .connection import Base


class SeccionBoletin(Base):
    __tablename__ = 'seccion_boletin'

    titulo = Column(String(1000), primary_key=True)
    slug = Column(Text)
    date = Column(Date, primary_key=True)
    url = Column(Text)
    file_path = Column(Text)
    content = Column(Text)

    def __repr__(self):
        return "<SeccionBoletin: id='%d', titulo='%s', date='%s'>" % (self.id, self.titulo, self.date)
