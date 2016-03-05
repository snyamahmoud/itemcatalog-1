from flask import Flask, render_template
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_schema import Base, Category, Product

app = Flask(__name__)

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# TODO
# Fake products to test navigation; delete from live version.
product = {'name': 'Shoes',
           'description': 'Running shoes.',
           'price': '$115.99',
           'category_id': '1',
           'id': '1'}

products = [{'name': 'Shoes',
             'description': 'Running shoes.',
             'price': '$115.99',
             'category_id': '1',
             'id': '1'},
            {'name': 'Suit',
             'description': 'Swim suit.',
             'price': '$34.99',
             'category_id': '2',
             'id': '2'},
            {'name': 'Sunglasses',
             'description': 'Black sunglasses.',
             'price': '$15.99',
             'category_id': '3',
             'id': '3'}]


def GetAllCategories():
    """ Get a list of all categories in the catalog.

    Returns:
        categories: a list of Category tuples of all categories in the catalog.
    """
    categories = session.query(Category).order_by(Category.name)
    return categories


@app.route('/')
@app.route('/catalog/')
def categoryListing():
    return render_template('list_all_categories.html',
                           categories=GetAllCategories(),
                           products=products)


@app.route('/catalog/<int:category_id>/add/')
def addCategory(category_id):
    return render_template('add_category.html',
                           categories=GetAllCategories())


@app.route('/catalog/<int:category_id>/edit/')
def editCategory(category_id):
    return render_template('edit_category.html',
                           categories=GetAllCategories())


@app.route('/catalog/<int:category_id>/delete/')
def deleteCategory(category_id):
    return render_template('delete_category.html',
                           categories=GetAllCategories())


@app.route('/catalog/<int:category_id>/')
def productListing(category_id):
    return render_template('list_all_products.html',
                           categories=GetAllCategories(),
                           products=products)


@app.route('/catalog/<int:category_id>/<int:product_id>/view/')
def viewProduct(category_id, product_id):
    return render_template('view_product.html',
                           categories=GetAllCategories(),
                           product=product)


@app.route('/catalog/<int:category_id>/<int:product_id>/add/')
def addProduct(category_id, product_id):
    return render_template('add_product.html',
                           categories=GetAllCategories())


@app.route('/catalog/<int:category_id>/<int:product_id>/edit/')
def editProduct(category_id, product_id):
    return render_template('edit_product.html',
                           categories=GetAllCategories())


@app.route('/catalog/<int:category_id>/<int:product_id>/delete/')
def deleteProduct(category_id, product_id):
    return render_template('delete_product.html',
                           categories=GetAllCategories())


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
