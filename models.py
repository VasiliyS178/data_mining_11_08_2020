from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table, create_engine
)

Base = declarative_base()


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    writer_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship('Writer', back_populates='post')

    def __init__(self, title:str, url:str, writer_id):
        self.title = title
        self.url = url
        self.writer_id = writer_id


class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=False, nullable=False)
    url = Column(String, unique=True, nullable=False)
    post = relationship('Post', back_populates='writer')

    def __init__(self, name, url):
        self.name = name
        self.url = url


if __name__ == '__main__':
    engine = create_engine('sqllite:////bg_blog.db')
    Base.metadata.create_all(engine)

    session_db = sessionmaker(bind=engine)

    session = session_db()
    writers = [Writer(f'name {itm}', f'url/{itm}') for itm in range(1, 30)]
    session.add_all(writers)
    try:
        session.commit()
    except Exception as e:
        print(e)
        session.rollback()
    finally:
        session.close()

    # Выборка всех авторов с id = 2
    session.query(Writer).filter(Writer.id == 2).all()
    session.query(Writer).filter_by(id=2).all()
