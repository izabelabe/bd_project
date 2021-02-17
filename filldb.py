import re
import requests
from PIL import Image
import MySQLdb
import os
import scraping

# database connection variables
HOST = "localhost"
USERNAME = "root"
PASSWORD = "qazxcde1322"
DATABASE = "product_db"



db = MySQLdb.connect(HOST, USERNAME, PASSWORD, DATABASE)
if (db):
    print("Połączenie ustanowione")
cursor = db.cursor()

barcode = ''
max_val = 9999999999999
val = 3

while val < max_val:
    image = None
    barcode = str(val)
    item = scraping.parse_product((13-len(barcode))*'0' + barcode)
    if item is not None:
        if item['im'] is not None:
            item['im'].save(item['barcode'] + ".jpeg")
            with open(item['barcode'] + ".jpeg", 'rb') as file:
                image = file.read()
            os.remove(item['barcode']+".jpeg")
        try:
            sql = "INSERT INTO products (barcode, name, producer, calories, fat, saturatedFat, carbohydrates, sugar, proteins, salt, image, ingredients, nutriscore) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql, (
            item['barcode'], item['product_name'], item['producer'], item['kcal'], item['fat'], item['saturated_fat'],
            item['carbs'], item['sugar'], item['protein'], item['salt'], image, item['ingredients'], item['nutri_score']))

            db.commit()
            adds = scraping.get_pubchem_adds(item['adds'])
            for add in adds:
                check = "SELECT * from components where cid = %s"
                cursor.execute(check, (add['cid'], ))

                if cursor.fetchone() is None:
                    sql2 = "INSERT INTO components (cid, name, synonyms, molecular_formula, molecular_weight, canonical_smiles) VALUES (%s,%s,%s,%s,%s,%s)"

                    cursor.execute(sql2, (add['cid'], add['name'], add['synonyms'], add['molecular_formula'],
                                          add['molecular_weight'], add['canonical_smiles']))

                    db.commit()

                relation = "INSERT INTO products_components (product_id,component_id) VALUES (%s,%s)"
                cursor.execute(relation, (item['barcode'], add['cid']))
                db.commit()

        except:
            db.rollback()

    val = val + 1

    #można by było execute many i wtedy tylko raz db.commit ale frankly juz napisalam tak to tak bedzie
"""
sql_fetch_blob_query = ""SELECT * from products where barcode = '0000000000024'""
cursor.execute(sql_fetch_blob_query)

photo = cursor.fetchone()[10]
with open("text.jpeg", "wb") as File:
    File.write(photo)
    File.close()
"""