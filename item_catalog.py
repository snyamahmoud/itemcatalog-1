from flask import Flask

app = Flask(__name__)


@app.route('/')
@app.route('/catalog/')
def categoryListing():
    return "categoryListing page"


@app.route('/catalog/<int:category_id>/add/')
def addCategory(category_id):
    return "addCategory page"


@app.route('/catalog/<int:category_id>/edit/')
def editCategory(category_id):
    return "editCategory page"


@app.route('/catalog/<int:category_id>/delete/')
def deleteCategory(category_id):
    return "deleteCategory page"


@app.route('/catalog/<int:category_id>/')
def productListing(category_id):
    return "productListing page"


@app.route('/catalog/<int:category_id>/<int:product_id>/add/')
def addProduct(category_id, product_id):
    return "addProduct page"


@app.route('/catalog/<int:category_id>/<int:product_id>/edit/')
def editProduct(category_id, product_id):
    return "editProduct page"


@app.route('/catalog/<int:category_id>/<int:product_id>/delete/')
def deleteProduct(category_id, product_id):
    return "deleteProduct page"


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
