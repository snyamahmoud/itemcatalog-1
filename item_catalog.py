from flask import Flask, render_template, url_for, request, redirect, jsonify
from flask import session as login_session
from flask import make_response
from flask import abort, g
from functools import wraps

from xml.etree.ElementTree import Element, SubElement, Comment, tostring

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_schema import Base, Category, Product, User

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

import random
import string
import httplib2
import json
import requests


app = Flask(__name__)


GOOGLE_CLIENT_ID = json.loads(
    open('client_secrets_google.json', 'r').read())['web']['client_id']

FACEBOOK_CLIENT_ID = json.loads(
    open('client_secrets_facebook.json', 'r').read())['web']['app_id']

FACEBOOK_CLIENT_SECRET = json.loads(
    open('client_secrets_facebook.json', 'r').read())['web']['app_secret']


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Category Helper Methods -----------------------------------------------------


def GetAllCategories():
    """ Get a list of all categories in the catalog.

    Returns:
        categories: a list of Category tuples of all categories in the catalog.
    """
    categories = session.query(Category).order_by(Category.name)
    return categories


def GetSingleCategory(category_id):
    """ Get a single category.

    Args:
        category_id: the ID of the category to get.
    Returns:
        singleCategory: a Category object.
    """
    singleCategory = session.query(Category).filter_by(id=category_id).one()
    return singleCategory


# Product Helper Methods ------------------------------------------------------


def GetAllProducts(category_id):
    """ Get a list of all products in a category.

    Args:
        category_id: the ID of the category to get the products for.
    Returns:
        products: a list of Product tuples of all products in a category.
    """
    if category_id == 0:
        products = session.query(Product).\
            order_by(Product.category_id, Product.id)
    else:
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


# User Helper Methods ---------------------------------------------------------


def CreateUser(login_session):
    """ Create a new user from the current session.

    Args:
        login_session: the current session.
    Returns:
        user.id: the ID of the new user that was created.
    """
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'],
                   provider=login_session['provider'])
    session.add(newUser)
    session.commit()

    user = session.query(User).filter_by(email=login_session['email'],
                                         provider=login_session['provider']).one()
    return user.id


def GetUserIDFromEmail(email):
    """ Attempt to find a user in the db using an email address.

    Args:
        email: the email of the user that you want to find.
    Returns:
        user: if the user is found a user id is returned.
        None: if the user is not found then None is returned.
    """
    try:
        user = session.query(User).filter_by(email=email,
                                             provider=login_session['provider']).one()
        return user.id
    except:
        return None


def GetUserIDFromLoginSession():
    """ Attempt to find a user in the db using the current session.

    Returns:
        user: if the user is found a user id is returned.
        None: if the user is not found then None is returned.
    """
    if 'user_id' in login_session:
        return login_session['user_id']
    return None


def GetUserInfo(user_id):
    """ Get user information from the db.

    Args:
        user_id: the ID of the user to get.
    Returns:
        user: a User object.
    """
    if user_id is None:
        return None
    user = session.query(User).filter_by(id=user_id).one()
    return user


# Login Helper Methods --------------------------------------------------------


def LoginRequired(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('userLogin', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def ConnectUser():
    """ Handles user login from any provider.

     - verify the state token
     - exchange token for credentials
     - verify the credentials
     - ensure the user is not already logged in
     - store user data in local session
     - welcome the user
    """
    if 'provider' not in login_session:
        response = make_response(json.dumps('Provider not defined.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Ensure that the state token from the client matches
    # the state token on the server.
    if request.args.get('state') != login_session['state']:
        # If the tokens don't match, notify the user and exit.
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if login_session['provider'] == 'google':
        # Obtain authorization code from the details the client submitted.
        auth_code = request.data

        try:
            # Exchange the authorization code for a credentials object.
            oauth_flow = flow_from_clientsecrets(
                'client_secrets_google.json', scope='')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(auth_code)
        except FlowExchangeError:
            # Something went wrong in the exchange process,
            # notify the user and exit.
            response = make_response(
                json.dumps('Failed to exchange the authorization code for a credentials object.'), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify that the access token is valid.
        access_token = credentials.access_token
        url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
               % access_token)
        h = httplib2.Http()
        result = json.loads(h.request(url, 'GET')[1])

        # If there was an error in the access token info, abort.
        if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')), 500)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify that the access token is used for the intended user.
        gplus_id = credentials.id_token['sub']
        if result['user_id'] != gplus_id:
            response = make_response(
                json.dumps("Token's user ID doesn't match given user ID."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify that the access token is valid for this app.
        if result['issued_to'] != GOOGLE_CLIENT_ID:
            response = make_response(
                json.dumps("Token's client ID does not match app's."), 401)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Verify the user is not already logged in.
        stored_credentials = login_session.get('credentials')
        stored_gplus_id = login_session.get('gplus_id')
        if stored_credentials is not None and gplus_id == stored_gplus_id:
            response = make_response(json.dumps('You are already logged in! Redirecting ...'),
                                     200)
            response.headers['Content-Type'] = 'application/json'
            return response

        # Store the access token and user creds in the session for later use.
        login_session['credentials'] = credentials.access_token
        login_session['gplus_id'] = gplus_id

        # Use the Goolge Plus API to get more info about the user.
        userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
        params = {'access_token': credentials.access_token, 'alt': 'json'}
        answer = requests.get(userinfo_url, params=params)

        # Save the user data to a json object.
        data = answer.json()

        # Store the user data in the login session.
        login_session['username'] = data['name']
        login_session['picture'] = data['picture']
        login_session['email'] = data['email']

    elif login_session['provider'] == 'facebook':
        # Exchange short-lived token for long-lived token.
        access_token = request.data
        url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
            FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET, access_token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]

        # Strip expire tag from long-lived token.
        token = result.split("&")[0]

        # Use token to get user data from API.
        url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]

        # Save the user data to a json object.
        data = json.loads(result)

        # Store the user data in the login session.
        login_session['username'] = data["name"]
        login_session['email'] = data["email"]
        login_session['facebook_id'] = data["id"]

        # The token must be stored in the login_session in
        # order to properly logout. Strip out the information
        # before the equals sign in the token.
        stored_token = token.split("=")[1]
        login_session['access_token'] = stored_token

        # Get user picture.
        url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]

        # Save the user picture to a json object.
        data = json.loads(result)

        # Store the user picture in the login session.
        login_session['picture'] = data["data"]["url"]

    # Determine if the user exists, if it doesn't then create a new one.
    user_id = GetUserIDFromEmail(login_session['email'])
    if user_id is None:
        user_id = CreateUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<img class="float-left" src="'
    output += login_session['picture']
    output += ' " style = "width: 40px; height: 40px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    output += '<h3 class="float-left">Welcome, '
    output += login_session['username']
    output += '!</h3>'
    return output


# CSRF Helper Methods ---------------------------------------------------------


def ValidateNonce():
    """ Validate the CSRF token and abort if it's invalid. """
    token = login_session.pop('csrf_token', None)
    if not token or token != request.form.get('csrf_token'):
        abort(403)


def GenerateNonce():
    """ Generate a CSRF token. """
    if 'csrf_token' not in login_session:
        login_session['csrf_token'] = '%030x' % random.randrange(16**30)
    return login_session['csrf_token']


# Login / Logout Routing Methods ----------------------------------------------


@app.route('/login/')
def userLogin():
    """ Display the login page of the catalog.

    Returns:
        The login page of the catalog.
    """
    # Generate an anti forgery state token.
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    # Add the state token to the current login session.
    login_session['state'] = state
    return render_template('login.html',
                           google_client_id=GOOGLE_CLIENT_ID,
                           facebook_client_id=FACEBOOK_CLIENT_ID,
                           state_token=state)


@app.route('/googleConnect', methods=['POST'])
def googleConnect():
    """ Login the user using Google credentials. """
    login_session['provider'] = 'google'
    return ConnectUser()


@app.route('/facebookConnect', methods=['POST'])
def facebookConnect():
    """ Login the user using Facebook credentials. """
    login_session['provider'] = 'facebook'
    return ConnectUser()


@app.route('/logout/')
def userLogout():
    """ Logout the user from the provider that they logged in with."""
    if login_session['provider'] == 'google':
        access_token = None

        if login_session:
            if 'credentials' in login_session:
                access_token = login_session['credentials']

        if access_token is None:
            # No one is logged in, abort.
            print 'Access Token is None'
            response = make_response(json.dumps(
                'Current user not connected.'), 401)
            response.headers['Content-Type`'] = 'application/json'
            return redirect(url_for('categoryListing'))

        # Use Google API to revoke the token.
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
        h = httplib2.Http()

        # Grab the result from Google.
        result = h.request(url, 'GET')[0]

        if result['status'] == '200':
            # Success, user was logged out.
            del login_session['credentials']
            del login_session['gplus_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            print "success logout"
            response = make_response(json.dumps(
                'Successfully disconnected.'), 200)
            response.headers['Content-Type'] = 'application/json'
            return redirect(url_for('categoryListing'))
        else:
            # Something went wrong, notify the user.
            print "FAIL logout"
            response = make_response(json.dumps(
                result, 400))
            response.headers['Content-Type'] = 'application/json'
            return response

    elif login_session['provider'] == 'facebook':
        facebook_id = login_session['facebook_id']
        url = 'https://graph.facebook.com/%s/permissions' % facebook_id
        h = httplib2.Http()
        result = h.request(url, 'DELETE')[1]

        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['facebook_id']
        print "success logout"
        response = make_response(json.dumps(
            'Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('categoryListing'))


# Category Routing Methods ----------------------------------------------------


@app.route('/')
@app.route('/catalog/')
def categoryListing():
    """ Display the home page of the catalog.

    Returns:
        The home page of the catalog.
    """
    user_id = None
    if 'user_id' in login_session:
        user_id = login_session['user_id']

    return render_template('list_all_categories.html',
                           categories=GetAllCategories(),
                           products=GetLatestProducts(),
                           user=GetUserInfo(GetUserIDFromLoginSession()))


@app.route('/catalog/add/',
           methods=['GET', 'POST'])
@LoginRequired
def addCategory():
    """ Add a category to the catalog. Supports GET and POST.

    Returns:
        GET: the New Category form.
        POST: the product listing for the new category.
    """
    if request.method == 'POST':
        ValidateNonce()

        if request.form['name']:
            newCategory = Category(name=request.form['name'],
                                   user_id=login_session['user_id'])
        session.add(newCategory)
        session.commit()
        return redirect(url_for('productListing',
                                category_id=newCategory.id))
    else:
        return render_template('add_category.html',
                               categories=GetAllCategories(),
                               user=GetUserInfo(GetUserIDFromLoginSession()),
                               csrf_token=GenerateNonce())


@app.route('/catalog/<int:category_id>/edit/',
           methods=['GET', 'POST'])
@LoginRequired
def editCategory(category_id):
    """ Edit a category. Supports GET and POST.

    Args:
        category_id: the ID of the category to edit.
    Returns:
        GET: the Edit Category form.
        POST: the product listing for the edited category.
    """
    editedCategory = GetSingleCategory(category_id)

    if login_session['user_id'] != editedCategory.user.id:
        return redirect(url_for('userLogin'))

    if request.method == 'POST':
        ValidateNonce()

        if request.form['name']:
            editedCategory.name = request.form['name']
        session.add(editedCategory)
        session.commit()
        return redirect(url_for('productListing',
                                category_id=editedCategory.id))
    else:
        return render_template('edit_category.html',
                               categories=GetAllCategories(),
                               editedCategory=editedCategory,
                               user=GetUserInfo(GetUserIDFromLoginSession()),
                               csrf_token=GenerateNonce())


@app.route('/catalog/<int:category_id>/delete/',
           methods=['GET', 'POST'])
@LoginRequired
def deleteCategory(category_id):
    """ Delete a category. Supports GET and POST.

    Args:
        category_id: the ID of the category to delete.
    Returns:
        GET: the Delete Category form.
        POST: the home page of the catalog.
    """
    deletedCategory = GetSingleCategory(category_id)

    if login_session['user_id'] != deletedCategory.user.id:
        return redirect(url_for('userLogin'))

    if request.method == 'POST':
        ValidateNonce()

        session.delete(deletedCategory)
        session.commit()
        return redirect(url_for('categoryListing'))
    else:
        return render_template('delete_category.html',
                               categories=GetAllCategories(),
                               deletedCategory=deletedCategory,
                               user=GetUserInfo(GetUserIDFromLoginSession()),
                               csrf_token=GenerateNonce())


# Product Routing Methods -----------------------------------------------------


@app.route('/catalog/<int:category_id>/')
def productListing(category_id):
    """ List all products for a category.

    Args:
        category_id: the ID of the category to get the product listing for.
    Returns:
        The product listing for the selected category.
    """
    listCategory = GetSingleCategory(category_id)
    return render_template('list_all_products.html',
                           categories=GetAllCategories(),
                           listCategory=listCategory,
                           products=GetAllProducts(category_id),
                           user=GetUserInfo(GetUserIDFromLoginSession()))


@app.route('/catalog/<int:category_id>/<int:product_id>/view/')
def viewProduct(category_id, product_id):
    """ View the details of the selected product.

    Args:
        category_id: the ID of the category that the product is in.
        product_id: the ID of the selected product.
    Returns:
        A page with the product details.
    """
    return render_template('view_product.html',
                           categories=GetAllCategories(),
                           singleproduct=GetSingleProduct(product_id),
                           user=GetUserInfo(GetUserIDFromLoginSession()))


@app.route('/catalog/<int:category_id>/add/',
           methods=['GET', 'POST'])
@LoginRequired
def addProduct(category_id):
    """ Add a product to the selected category.

    Args:
        category_id: the ID of the category to add the product to.
    Returns:
        GET: the New Product form.
        POST: the product listing for the selected category.
    """
    if request.method == 'POST':
        ValidateNonce()

        if request.form['name']:
            newProduct = Product(name=request.form['name'],
                                 description=request.form['description'],
                                 price=request.form['price'],
                                 category_id=category_id,
                                 user_id=login_session['user_id'])
        session.add(newProduct)
        session.commit()
        return redirect(url_for('productListing',
                                category_id=category_id))
    else:
        return render_template('add_product.html',
                               categories=GetAllCategories(),
                               category_id=category_id,
                               user=GetUserInfo(GetUserIDFromLoginSession()),
                               csrf_token=GenerateNonce())


@app.route('/catalog/<int:category_id>/<int:product_id>/edit/',
           methods=['GET', 'POST'])
@LoginRequired
def editProduct(category_id, product_id):
    """ Edit a product.

    Args:
        category_id: the ID of the category that the product is in.
        product_id: the ID of the selected product.
    Returns:
        GET: the Edit Product form.
        POST: the product listing for the selected category.
    """
    editedProduct = GetSingleProduct(product_id)

    if login_session['user_id'] != editedProduct.user.id:
        return redirect(url_for('userLogin'))

    if request.method == 'POST':
        ValidateNonce()

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
                               editedProduct=editedProduct,
                               user=GetUserInfo(GetUserIDFromLoginSession()),
                               csrf_token=GenerateNonce())


@app.route('/catalog/<int:category_id>/<int:product_id>/delete/',
           methods=['GET', 'POST'])
@LoginRequired
def deleteProduct(category_id, product_id):
    """ Delete a product.

    Args:
        category_id: the ID of the category that the product is in.
        product_id: the ID of the selected product.
    Returns:
        GET: the Delete Product form.
        POST: the product listing for the selected category.
    """
    deletedProduct = GetSingleProduct(product_id)

    if login_session['user_id'] != deletedProduct.user.id:
        return redirect(url_for('userLogin'))

    if request.method == 'POST':
        ValidateNonce()

        session.delete(deletedProduct)
        session.commit()
        return redirect(url_for('productListing',
                                category_id=category_id))
    else:
        return render_template('delete_product.html',
                               categories=GetAllCategories(),
                               category_id=category_id,
                               deletedProduct=deletedProduct,
                               user=GetUserInfo(GetUserIDFromLoginSession()),
                               csrf_token=GenerateNonce())


# API Routing Methods ---------------------------------------------------------


@app.route('/catalog/apiList')
def apiList():
    """ A list of all available API links.

    Returns:
        A page containing links to API endpoints.
    """
    return render_template('api_list.html')


@app.route('/catalog/allcategories/json/')
def allCategoriesJSON():
    """ API endpoint for JSON GET request - All Categories.

    Returns:
        A JSON response containing all categories in the catalog.
    """
    categories = GetAllCategories()
    return jsonify(Category=[category.serialize for category in categories])


@app.route('/catalog/allProducts/json/')
def allProductsJSON():
    """ API endpoint for JSON GET request - All Products.

    Returns:
        A JSON response containing all products in the catalog.
    """
    products = GetAllProducts(0)
    return jsonify(Product=[product.serialize for product in products])


@app.route('/catalog/allcategories/xml/')
def allCategoriesXML():
    """ API endpoint for XML GET request - All Categories.

    Returns:
        An XML response containing all categories in the catalog.
    """
    top = Element('catalog')

    categories = GetAllCategories()

    for category in categories:
        category_root = SubElement(top, 'category')

        category_root_id = SubElement(category_root, 'id')
        category_root_id.text = str(category.id)

        category_root_name = SubElement(category_root, 'name')
        category_root_name.text = str(category.name)

    return render_template('xml_response.xml',
                           xml_string=tostring(top))


@app.route('/catalog/allProducts/xml/')
def allProductsXML():
    """ API endpoint for XML GET request - All Products.

    Returns:
        An XML response containing all products in the catalog.
    """
    top = Element('catalog')

    products = GetAllProducts(0)

    for product in products:
        product_root = SubElement(top, 'product')

        product_root_id = SubElement(product_root, 'id')
        product_root_id.text = str(product.id)

        product_root_name = SubElement(product_root, 'name')
        product_root_name.text = str(product.name)

        product_root_desc = SubElement(product_root, 'description')
        product_root_desc.text = str(product.description)

        product_root_price = SubElement(product_root, 'price')
        product_root_price.text = str(product.price)

        product_root_categoryid = SubElement(product_root, 'category_id')
        product_root_categoryid.text = str(product.category.id)

    return render_template('xml_response.xml',
                           xml_string=tostring(top))


# -----------------------------------------------------------------------------


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host="0.0.0.0", port=5000)
