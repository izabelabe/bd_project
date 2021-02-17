import re
import requests
from PIL import Image
import pymysql
import os
import scraping
import threading

# database connection variables
HOST = "localhost"
USERNAME = "root"
PASSWORD = ""
DATABASE = "test_db"

class ScrapingThread(threading.Thread):
    def __init__(self, threadId, minVal, maxVal):
        threading.Thread.__init__(self)
        self.threadId = threadId
        self.minVal = minVal
        self.maxVal = maxVal

    def run(self):
        get_products(self.threadId, self.minVal, self.maxVal)


def get_products(id, starting_val, ending_val):
    db = pymysql.connect(host=HOST, user=USERNAME, password=PASSWORD, db=DATABASE)
    if (db):
        print(f"Thread {id} connected")
    else:
        print(f"Thread {id} encountered error while connecting to database")
    cursor = db.cursor()
    barcode = ''
    val = starting_val

    while val < ending_val:
        image = None
        barcode = str(val)
        item = scraping.parse_product((13-len(barcode))*'0' + barcode)
        print(item)
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
                print('insertion error')
                db.rollback()

        val = val + 1



if __name__ == '__main__':
    n_threads = 10
    threads = []
    starting_value = 0
    step = 1000000000000
    ending_value = 1000
    for i in range(n_threads):
        threads.append(ScrapingThread(i, i*step + starting_value, i*step + starting_value + ending_value))
    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()