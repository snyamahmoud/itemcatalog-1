# Item Catalog

Welcome to the Item Catalog!

### Summary

The item catalog provides a listing of sports products. Users can login to the site via Google+ or Facebook. Once logged in users can add, edit or delete categories and products. Users cannot modify categories and products from other uers. API endpoints are available in JSON and XML.

### Pre-requisites

1. A virtual machine of your choice to host the database and the webserver. I used [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](https://www.vagrantup.com/downloads.html).
2. SQLite to host the item catalog database. [Download SQLite here](https://www.sqlite.org/download.html).
3. Python to run the database script and web server. [Download Python here](https://www.python.org/).

### Getting Started

1. Download the project files.

2. Open the root directory and locate **database_test_script.py**. This is the script to create and populate database. Execute the script:
```python
python database_test_script.py
```
3. In the root directory locate **item_catalog.py**. Launch the module to host the webserver:
```python
python item_catalog.py
```
4. Navigate to http://localhost:5000