from flask import Flask, render_template, url_for, request, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_schema import Base, Category, Product

app = Flask(__name__)

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def GetAllCategories():
    """ Get a list of all categories in the catalog.

    Returns:
        categories: a list of Category tuples of all categories in the catalog.
    """
    categories = session.query(Category).order_by(Category.name)
    return categories


def GetAllProducts(category_id):
    """ Get a list of all products in a category.

    Args:
        category_id: the ID of the category to get the products for.
    Returns:
        products: a list of Product tuples of all products in a category.
    """
    products = session.query(Product).\
        filter_by(category_id=category_id).\
        order_by(Product.name)
    return products


def GetLatestProducts():
    """ Get a list of the last 5 products that were added.

    Returns:
        products: a list of Product tuples of the last 5 products added.
    """
    products = session.query(Product).order_by(Product.id.desc()).limit(5)
    return products


def GetSingleProduct(product_id):
    """ Get a single product.

    Args:
        product_id: the ID of the product to get.
    Returns:
        singleProduct: a Product object.
    """
    singleProduct = session.query(Product).filter_by(id=product_id).one()
    return singleProduct


@app.route('/')
@app.route('/catalog/')
def categoryListing():
    return render_template('list_all_categories.html',
                           categories=GetAllCategories(),
                           products=GetLatestProducts())


@app.route('/catalog/add/',
           methods=['GET', 'POST'])
def addCategory():
    if request.method == 'POST':
        if request.form['name']:
            newCategory = Category(name=request.form['name'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('productListing',
                                category_id=newCategory.id))
    else:
        return render_template('add_category.html',
                               categories=GetAllCategories())


@app.route('/catalog/<int:category_id>/edit/',
           methods=['GET', 'POST'])
def editCategory(category_id):
    editedCategory = session.query(Category).filter_by(id=category_id).one()

    if request.method == 'POST':
        if request.form['name']:
            editedCategory.name = request.form['name']
        session.add(editedCategory)
        session.commit()
        return redirect(url_for('productListing',
                                category_id=editedCategory.id))
    else:
        return render_template('edit_category.html',
                               categories=GetAllCategories(),
                               editedCategory=editedCategory)


@app.route('/catalog/<int:category_id>/delete/',
           methods=['GET', 'POST'])
def deleteCategory(category_id):
    deletedCategory = session.query(Category).filter_by(id=category_id).one()

    if request.method == 'POST':
        session.delete(deletedCategory)
        session.commit()
        return redirect(url_for('categoryListing'))
    else:
        return render_template('delete_category.html',
                               categories=GetAllCategories(),
                               deletedCategory=deletedCategory)


@app.route('/catalog/<int:category_id>/')
def productListing(category_id):
    listCategory = session.query(Category).filter_by(id=category_id).one()
    return render_template('list_all_products.html',
                           categories=GetAllCategories(),
                           listCategory=listCategory,
                           products=GetAllProducts(category_id))


@app.route('/catalog/<int:category_id>/<int:product_id>/view/')
def viewProduct(category_id, product_id):
    return render_template('view_product.html',
                           categories=GetAllCategories(),
                           singleproduct=GetSingleProduct(product_id))


@app.route('/catalog/<int:category_id>/add/',
           methods=['GET', 'POST'])
def addProduct(category_id):
    if request.method == 'POST':
        if request.form['name']:
            newProduct = Product(name=request.form['name'],
                                 description=request.form['description'],
                                 price=request.form['price'],
                                 category_id=category_id)
        session.add(newProduct)
        session.commit()
        return redirect(url_for('productListing',
                                category_id=category_id))
    else:
        return render_template('add_product.html',
                               categories=GetAllCategories(),
                               category_id=category_id)


@app.route('/catalog/<int:category_id>/<int:product_id>/edit/',
           methods=['GET', 'POST'])
def editProduct(category_id, product_id):
    editedProduct = GetSingleProduct(product_id)

    if request.method == 'POST':
        if request.form['name']:
            editedProduct.name = request.form['name']
            editedProduct.description = request.form['description']
            editedProduct.price = request.form['price']
        session.add(editedProduct)
        session.commit()
        return redirect(url_for('productListing',
                                category_id=editedProduct.category_id))
    else:
        return render_template('edit_product.html',
                               categories=GetAllCategories(),
                               editedProduct=editedProduct)


@app.route('/catalog/<int:category_id>/<int:product_id>/delete/',
           methods=['GET', 'POST'])
def deleteProduct(category_id, product_id):
    deletedProduct = GetSingleProduct(product_id)

    if request.method == 'POST':
        session.delete(deletedProduct)
        session.commit()
        return redirect(url_for('productListing',
                                category_id=category_id))
    else:
        return render_template('delete_product.html',
                               categories=GetAllCategories(),
                               category_id=category_id,
                               deletedProduct=deletedProduct)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
