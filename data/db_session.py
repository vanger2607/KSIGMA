import sqlalchemy as sql
import sqlalchemy.orm as orm
import sqlalchemy.ext.declarative as dec

Database = dec.declarative_base()
__factory = None


def global_init(file: str):
    global __factory
    if __factory:
        return
    if not file or not file.strip():
        raise Exception('Укажите файл')
    connection = f'sqlite:///{file.strip()}?check_same_thread=False'
    print('Connection success')
    engine = sql.create_engine(connection, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    from . import __all_models
    Database.metadata.create_all(engine)


def create_session():
    global __factory
    return __factory()
