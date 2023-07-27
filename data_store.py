import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session


from config import db_url_object

metadata = MetaData()
Base = declarative_base()

engine = create_engine(db_url_object)


class Viewed(Base):
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)


class WorksheetsBD:
    def __init__(self, engine):
        self.engine = engine

    # Добавление записи в базу данных
    def add_user(self, profile_id, worksheet_id):
        with Session(self.engine) as session:
            to_bd = Viewed(profile_id=profile_id, worksheet_id=worksheet_id)
            session.add(to_bd)
            session.commit()

    # Извлечение записей из БД
    def check_user(self, profile_id, worksheet_id):
        with Session(self.engine) as session:
            from_bd = session.query(Viewed).filter(
                Viewed.profile_id == profile_id,
                Viewed.worksheet_id == worksheet_id
            ).first()
            return True if from_bd else False


if __name__ == '__main__':
    engine = create_engine(db_url_object)
    Base.metadata.create_all(engine)
    # WorksheetsBD.add_user(engine, 2113, 39712308)
    # res = WorksheetsBD.check_user(engine, 2113, 39712308)
    # print(res)
