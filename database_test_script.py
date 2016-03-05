from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_schema import Base, Category, Product


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def AddCategory(category_name):
    category = Category(name=category_name)
    session.add(category)
    session.commit()
    return category.id


def AddProduct(product_name,
               product_description,
               product_price,
               product_category_id
               ):
    product = Product(name=product_name,
                      description=product_description,
                      price=product_price,
                      category_id=product_category_id)
    session.add(product)
    session.commit()


category_id = AddCategory("Swimming")

AddProduct("Suit",
           "Blue and yellow racerback.",
           39.95,
           category_id)

AddProduct("Goggles",
           "Sleek and stylish. Designed for optimum comfort.",
           21.50,
           category_id)

AddProduct("Cap",
           "Comes in a variety of colours. Men's and Women's. S, M, L.",
           5.75,
           category_id)


category_id = AddCategory("Running")

AddProduct("Ultra Lite Shoes",
           "Racing detail, superior comfort.",
           109.95,
           category_id)

AddProduct("Hat",
           "Mesh sides wick away sweat.",
           32.95,
           category_id)

AddProduct("Socks",
           "Synthetic blend.",
           11.97,
           category_id)


category_id = AddCategory("Gym and Training")
category_id = AddCategory("Tennis")
category_id = AddCategory("Football")
category_id = AddCategory("Baseball")
category_id = AddCategory("Soccer")
category_id = AddCategory("Basketball")
category_id = AddCategory("Hockey")
category_id = AddCategory("Yoga")
