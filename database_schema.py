import os
import sys

# To support mapper code.
from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint

# Inherit from base class.
from sqlalchemy.ext.declarative import declarative_base

# To create FK.
from sqlalchemy.orm import relationship

# To connect to the db engine.
from sqlalchemy import create_engine


# An instance of the SQLA base class.
# Tells SQLA that the classes are special SQLA classes that map to db tables.
Base = declarative_base()


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

    # Names need to be unique to support vanity URLs.
    unique_category_name = UniqueConstraint('name')


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    price = Column(Float)

    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    # Names need to be unique to a category to support vanity URLs.
    unique_product_name = UniqueConstraint('category_id', 'name')


# Connect to the db engine.
engine = create_engine('sqlite:///itemcatalog.db')

# Create a db and all required tables.
Base.metadata.create_all(engine)
