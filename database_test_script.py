from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_schema import Base, Category, Product, User


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def AddCategory(category_name,
                user_id):
    category = Category(name=category_name,
                        user_id=user_id)
    session.add(category)
    session.commit()
    return category.id


def AddProduct(product_name,
               product_description,
               product_price,
               product_category_id,
               product_user_id
               ):
    product = Product(name=product_name,
                      description=product_description,
                      price=product_price,
                      category_id=product_category_id,
                      user_id=product_user_id)
    session.add(product)
    session.commit()


def AddUser(user_name,
            user_email):
    user = User(name=user_name,
                email=user_email)
    session.add(user)
    session.commit()
    return user.id


user_id = AddUser("Jenny",
                  "jenny@jenny.ca")


category_id = AddCategory("Swimming", user_id)

AddProduct("Suit",
           "Blue and yellow racerback.",
           39.95,
           category_id,
           user_id)

AddProduct("Goggles",
           "Sleek and stylish. Designed for optimum comfort.",
           21.50,
           category_id,
           user_id)

AddProduct("Cap",
           "Comes in a variety of colours. Men's and Women's. S, M, L.",
           5.75,
           category_id,
           user_id)


category_id = AddCategory("Running", user_id)

AddProduct("Ultra Lite Shoes",
           "Racing detail, superior comfort.",
           109.95,
           category_id,
           user_id)

AddProduct("Hat",
           "Mesh sides wick away sweat.",
           32.95,
           category_id,
           user_id)

AddProduct("Socks",
           "Synthetic blend.",
           11.97,
           category_id,
           user_id)


category_id = AddCategory("Gym and Training", user_id)
category_id = AddCategory("Tennis", user_id)
category_id = AddCategory("Football", user_id)
category_id = AddCategory("Baseball", user_id)
category_id = AddCategory("Soccer", user_id)
category_id = AddCategory("Basketball", user_id)
category_id = AddCategory("Hockey", user_id)
category_id = AddCategory("Yoga", user_id)

print "database populated."
