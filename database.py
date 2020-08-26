from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Post, Writer

if __name__ == '__main__':
    engine = create_engine('sqllite:///gb_blog.db')
    Base.metadata.create_all(engine)

    session_db = sessionmaker(bind=engine)

    session = session_db()

    writers = [Writer(f'name {itm}', f'url/{itm}') for itm in range(1, 30)]
    # Добавление в сессию записи по 1 шт.
    # for itm in writers:
    #     session.add(itm)
    session.add_all(writers)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
    finally:
        session.close()

    # Выбор всех writers по условию
    session.query(Writer).filter(Writer.id == 2).all()
    session.query(Writer).filter_by(id=2).all()

