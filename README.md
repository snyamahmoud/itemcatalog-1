# Item Catalog

Welcome to the Item Catalog!

### Summary

The item catalog provides a listing of sports products. Users can login to the site via Google+ or Facebook. Once logged in users can add, edit or delete categories and products. Users cannot modify categories and products from other uers. API endpoints are available in JSON and XML.

### Pre-requisites

1. A virtual machine of your choice to host the database and the webserver. I used [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](https://www.vagrantup.com/downloads.html).
2. [SQLite](https://www.sqlite.org/download.html) to host the item catalog database.
3. [Python](https://www.python.org/) to run the database script and web server.
4. A client ID and client secret from either [Google+](https://developers.google.com/) or [Facebook](https://developers.facebook.com/docs/apps/register).

### Getting Started

1. Download the project files.

2. Open the root directory and locate **database_test_script.py**. This is the script to create and populate the database. Execute the script:
```python
python database_test_script.py
```
3. Now you'll need to save your client ID and client secret from your Google+ or Facebook account into the appropriate config file.

#### Google+
In the root directory locate **client_secrets_google.json**. Enter your client ID, client secret and project ID in the appropriate fields.
```json
{
    "web":
    {
        "client_id":"YOUR_CLIENT_ID",
        "client_secret":"YOUR_CLIENT_SECRET",

        "project_id":"YOUR_PROJECT_ID",
``` 

### Facebook
In the root directory locate **client_secrets_facebook.json**. Enter your client ID and client secret in the appropriate fields.
```json
{
    "web":
    {
        "app_id": "YOUR_CLIENT_ID",
        "app_secret": "YOUR_CLIENT_SECRET"
    }
}
``` 

4. In the root directory locate **item_catalog.py**. Launch the module to host the webserver:
```python
python item_catalog.py
```
5. Navigate to http://localhost:5000