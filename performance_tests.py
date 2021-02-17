import pymysql
import os
import scraping
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, Table, String, ForeignKey, LargeBinary, Text, Float
from sqlalchemy.orm import relationship, backref
import time

# database connection variables
HOST = "localhost"
USERNAME = "root"
PASSWORD = ""
DATABASE = "test_db"

engine = create_engine('mysql+pymysql://'+USERNAME+':'+PASSWORD+'@'+HOST+'/'+DATABASE)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

products_components = Table('products_components', Base.metadata,
                                Column('product_id', String(13), ForeignKey('products.barcode')),
                                Column('component_id', Integer, ForeignKey('components.cid'))
                                )

class Product(Base):
    __tablename__ = 'products'

    barcode = Column(String(13), primary_key=True)
    name = Column(String(255), nullable=False)
    producer = Column(String(50), nullable=True)
    calories = Column(String(10), nullable=True)
    fat = Column(String(10), nullable=True)
    saturatedFat = Column(String(10), nullable=True)
    carbohydrates = Column(String(10), nullable=True)
    sugar = Column(String(10), nullable=True)
    proteins = Column(String(10), nullable=True)
    salt = Column(String(10), nullable=True)
    image = Column(LargeBinary, nullable=True)
    ingredients = Column(Text, nullable=True)
    nutriscore = Column(String(1), nullable=True)
    components = relationship("Component", secondary=products_components,
                                 backref=backref('prods', lazy='dynamic')
                                 )

    # def __repr__(self):
    #     return '<Barcode %r>' % self.barcode


class Component(Base):
    __tablename__ = 'components'

    cid = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=True)
    synonyms = Column(Text, nullable=True)
    molecular_formula = Column(String(50), nullable=True)
    molecular_weight = Column(Float, nullable=True)
    canonical_smiles = Column(String(50), nullable=True)

pydb = pymysql.connect(host=HOST, user=USERNAME, password=PASSWORD, db=DATABASE)
if (pydb):
    print("Connected")
cursor = pydb.cursor()

item = scraping.parse_product('5449000000996')
n = 10000
items = []

item['im'].save(item['barcode'] + ".jpeg")
with open(item['barcode'] + ".jpeg", 'rb') as file:
    image = file.read()
os.remove(item['barcode'] + ".jpeg")




def insert_sql():
    for i in range(n):
            sql = """INSERT INTO products (barcode, name, producer, calories, fat, saturatedFat, carbohydrates, 
            sugar, proteins, salt, image, ingredients, nutriscore) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(sql, (
                i, item['product_name'], item['producer'], item['kcal'], item['fat'], item['saturated_fat'],
                item['carbs'], item['sugar'], item['protein'], item['salt'], item['im'], item['ingredients'], item['nutri_score']))

    pydb.commit()

def insert_orm():
    for i in range(n):
        prod = Product(
            barcode=i,
            name=item['product_name'],
            calories=item['kcal'],
            fat=item['fat'],
            saturatedFat=item['saturated_fat'],
            carbohydrates=item['carbs'],
            sugar=item['sugar'],
            proteins=item['protein'],
            salt=item['salt'],
            ingredients=item['ingredients'],
            image=image
          )
        session.add(prod)
    session.commit()


def delete_sql():
    sql = "DELETE FROM products"
    cursor.execute(sql)
    pydb.commit()

def select_all_sql():
    sql = "SELECT * FROM products"
    result = cursor.execute(sql)

def select_all_orm():
    result = session.query(Product)

if __name__ == '__main__':
    delete_sql()

    print(f"Inserting {n} elements")
    start = time.time()
    insert_sql()
    stop = time.time()
    print(f"SQL {stop-start}")

    delete_sql()

    start = time.time()
    insert_orm()
    stop = time.time()
    print(f"ORM {stop - start}")

    print(f"Selecting {n} elements")
    start = time.time()
    select_all_sql()
    stop = time.time()
    print(f"SQL {stop - start}")

    start = time.time()
    select_all_orm()
    stop = time.time()
    print(f"ORM {stop - start}")

    delete_sql()
