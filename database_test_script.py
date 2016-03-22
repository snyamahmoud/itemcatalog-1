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
            user_email,
            user_provider):
    user = User(name=user_name,
                email=user_email,
                provider=user_provider)
    session.add(user)
    session.commit()
    return user.id


user_id = AddUser("Jenny",
                  "jenny@jenny.ca",
                  "hotmail")


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

AddProduct("Ab Crunch Machine",
           "Isolate ab muscles for a chiseled buff look.",
           469.99,
           category_id,
           user_id)

AddProduct("FTS 1000 - Foosball Table",
           "Awesome Christmas gift!",
           239.55,
           category_id,
           user_id)

AddProduct("Youth Boxing Gloves",
           "Yellow with black laces.",
           69.00,
           category_id,
           user_id)

AddProduct("Elliptical Cross Trainer",
           "Large cycle motion with rear drive.",
           1220.00,
           category_id,
           user_id)

category_id = AddCategory("Tennis", user_id)

AddProduct("Wilson Burn 95",
           "Headsize: 95in. String Pattern: 16x19. Swingweight: 335 (RDC). Length: 27.25",
           229.00,
           category_id,
           user_id)

AddProduct("Men's Tennis Hat Blue",
           "Blue mesh polyester, one size fits all.",
           20.00,
           category_id,
           user_id)


category_id = AddCategory("Football", user_id)

AddProduct("Mens Football Cleats",
           "",
           152.85,
           category_id,
           user_id)

AddProduct("Fleece Pullover",
           "Lightweight training hoodie.",
           95,
           category_id,
           user_id)


category_id = AddCategory("Baseball", user_id)

category_id = AddCategory("Soccer", user_id)

AddProduct("Padded Reversible Warmup Jacket",
           "Available in blue/black, red/brown.",
           145,
           category_id,
           user_id)

AddProduct("Men's Football Socks",
           "Available in M and L, various colours.",
           15.99,
           category_id,
           user_id)


category_id = AddCategory("Basketball", user_id)

AddProduct("Jordan Mini Ball (Size 3)",
           "Red and black.",
           14,
           category_id,
           user_id)

AddProduct("Men's Basketball Shorts",
           "",
           55.95,
           category_id,
           user_id)


category_id = AddCategory("Hockey", user_id)

AddProduct("CCM JetSpeed",
           "Senior, Junior and Youth",
           695.50,
           category_id,
           user_id)

AddProduct("Bauer Street Hockey stick (wood)",
           "",
           27.99,
           category_id,
           user_id)


category_id = AddCategory("Yoga", user_id)

AddProduct("Soft Dri Grip Mat (5mm)",
           "Superior wicking to prevent slipping.",
           74.98,
           category_id,
           user_id)

AddProduct("Grippy Yoga Mat Towel",
           "Absorbent microfibre top layer.",
           34.98,
           category_id,
           user_id)


print "database populated."
