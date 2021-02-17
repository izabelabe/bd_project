import os

from flask import Flask, render_template, request
from flaskext.mysql import MySQL
from flask_sqlalchemy import SQLAlchemy
import scraping
import sqlalchemy
import sys

app = Flask(__name__)
mysql = MySQL()
#konfiguracja połączenia z bazą
uri = 'mysql+pymysql://root:qazxcde1322@localhost/product_db'
app.config['SQLALCHEMY_DATABASE_URI'] = uri

# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = ''
# app.config['MYSQL_DATABASE_DB'] = 'products'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
db = SQLAlchemy(app)


products_components = db.Table('products_components',
                                db.Column('product_id', db.String(13), db.ForeignKey('products.barcode')),
                                db.Column('component_id', db.Integer, db.ForeignKey('components.cid'))
                                )
class Product(db.Model):
    __tablename__ = 'products'

    barcode = db.Column(db.String(13), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    producer = db.Column(db.String(50), nullable=True)
    calories = db.Column(db.String(10), nullable=True)
    fat = db.Column(db.String(10), nullable=True)
    saturatedFat = db.Column(db.String(10), nullable=True)
    carbohydrates = db.Column(db.String(10), nullable=True)
    sugar = db.Column(db.String(10), nullable=True)
    proteins = db.Column(db.String(10), nullable=True)
    salt = db.Column(db.String(10), nullable=True)
    image = db.Column(db.LargeBinary, nullable=True)
    ingredients = db.Column(db.Text, nullable=True)
    nutriscore = db.Column(db.String(1), nullable=True)
    components = db.relationship("Component", secondary=products_components,
                                 backref=db.backref('prods', lazy='dynamic')
                                 )

    # def __repr__(self):
    #     return '<Barcode %r>' % self.barcode


class Component(db.Model):
    __tablename__ = 'components'

    cid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=True)
    synonyms = db.Column(db.Text, nullable=True)
    molecular_formula = db.Column(db.String(50), nullable=True)
    molecular_weight = db.Column(db.Float, nullable=True)
    canonical_smiles = db.Column(db.String(50), nullable=True)

db.create_all()




@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        barcode = request.form['barcode']
        product = Product.query.filter_by(barcode=barcode).first()
        if product is not None:
            if product.image is not None:
                with open("./static/images/" + product.barcode + ".jpeg", "wb") as File:
                    File.write(product.image)
                    File.close()
                    image = product.barcode + ".jpeg"
            return render_template('index.html', isProduct=True, product=[product], found=True, image=image)


        try:
            item = scraping.parse_product(barcode)
            if item is None:
                return render_template('index.html', found=False)
            adds = scraping.get_pubchem_adds(item['adds'])
            image = None
            if item['im'] is not None:
                item['im'].save(item['barcode'] + ".jpeg")
                with open(item['barcode'] + ".jpeg", 'rb') as file:
                    image = file.read()
                os.remove(item['barcode'] + ".jpeg")

            new_product = Product(barcode=barcode,
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
            components = []
            for add in adds:
                comp = Component.query.filter_by(cid=add['cid']).first()
                if comp is None:
                    comp = Component(cid=add['cid'],
                                     name=add['name'],
                                     synonyms=add['synonyms'],
                                     molecular_formula=add['molecular_formula'],
                                     molecular_weight=add['molecular_weight'],
                                     canonical_smiles=add['canonical_smiles'])
                    db.session.add(comp)
                components.append(comp)

            db.session.add(new_product)
            for comp in components:
                new_product.components.append(comp)

            db.session.commit()
            if new_product.image is not None:
                with open("./static/images/" + new_product.barcode + ".jpeg", "wb") as File:
                    File.write(new_product.image)
                    File.close()
                    image = new_product.barcode + ".jpeg"

            return render_template('index.html', isProduct=True, product=[new_product], found=True, image=image)
        except:
            db.session.rollback()
            print("error")
            return render_template('index.html', isProduct=True, found=False)
    #GET
    else:
        if len(request.args) == 0:
            return render_template('index.html', isProduct=False)
        else:
            barcode = request.args.get('product')
            product = Product.query.filter_by(barcode=barcode)
            image = None
            if product.count() == 0:
                found = False
            else:
                found = True
                if product[0].image is not None:
                    with open("./static/images/"+product[0].barcode+".jpeg", "wb") as File:
                        File.write(product[0].image)
                        File.close()
                        image = product[0].barcode+".jpeg"

            return render_template('index.html', isProduct=True, product=product, found=found, image=image)




if __name__ == '__main__':
    app.run(debug=True)