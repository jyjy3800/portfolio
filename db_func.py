def dbengine(db):
    if db == 'mariadb':
        return  'mysql+pymysql://{}:{}@{}:{}/{}'
    elif db == 'oracle':
        return  'oracle+cx_oracle://{}:{}@{}:{}/{}'
    elif db == 'postgre':
        return  'postgresql+psycopg2://{}:{}@{}:{}/{}'