# MongoDB Quiz API

This project was created as part of the MongoDB Hackathon, it is a quiz API that provides the following functions:

- Authentication/ Authorization using OAuth2
- CRUD Operations for quiz categories
- CRUD Operations for quizzes
  - Including Quiz submition and calulating the total and reached points 
- Also, the project is fully covered by unit tests

## Description

An in-depth paragraph about your project and overview of use.

## Getting Started

This project is built on top of the Python FastApi framework using the awesome cloud based MongoDB Atlas database.


### Dependencies

This project is built on top of the Python FastApi framework using the awesome cloud based MongoDB Atlas database.

#### Tech Stack

- Python 3.9
- [FastApi](https://fastapi.tiangolo.com/)
- [MongoDB Cloud Atlas](https://www.mongodb.com/cloud/atlas)
- [MongoEngine](http://docs.mongoengine.org/index.html)


### Installing

#### 1. Clone the git repo:
```
git clone
```

#### 2. Download and install Python
To download python, please vistit this [link](https://www.python.org/downloads/).

For this project the following Python version was used: 3.9.* 

#### 3. Create a python virtual envrionment:
For more information on how to create please visit this [link](https://docs.python.org/3.9/library/venv.html).

#### 4. Install the required packages
````
pip install requirement.txt
````
For more information, please vist this [link](https://pip.pypa.io/en/stable/cli/pip_install/).

For a full list of all dependices, have a look at the file [requirements.txt](requirements.txt)

#### 5. Create the .env paramater file
Create a file named ".env"
Specify the parameters as needed:
````
AUTH_SECRET_KEY=MY_SECRET_KEY
AUTH_ALGORITHM=HS256
MONGODB_CONN_STR=mongodb+srv://dbuser:MY_DB_USER@MY_MONGODB_DATABASE?retryWrites=true&w=majority
````

For generating a secret key you can use the following command:
````
openssl rand -hex 32
````

### Executing program

To start the API use the following command:
````
python app.py
````
This should start a server listening on http://127.0.0.1:8000

After starting the server you can visit the OpenAPI definition (API Docs):
http://127.0.0.1:8000/docs

As previously mentioned, this projects contains unit tests. To execute the tests, use the following command:
````
pytest
````

Also, this project contains a [Postman Collection](tests/postman/Quiz%20API.postman_collection.json)

For more information on how to import a Postman Collection, please check out this [link](https://learning.postman.com/docs/getting-started/importing-and-exporting-data/#importing-postman-data).
After importing the Postman Collection, an [environment](https://learning.postman.com/docs/sending-requests/managing-environments/#creating-environments) must be created with the following parameters:
- api_url
  - API url
- username
  - Emailadress of your user (this address is used for authentication)
- password:
  - plain text password of your user

After creating the environment, the access token can be obtained (for more information, please visit this [link](https://learning.postman.com/docs/sending-requests/authorization/#oauth-20))
This step is important because some endpoints require authentication.
## Authors

Manuel Kanetscheider

## License

This project is licensed under the Apache-2 permissive license - see the [Licence file](LICENSE) for details.

## Acknowledgments

Inspiration, code snippets, etc.
* [Architecture Patterns with Python](https://www.oreilly.com/library/view/architecture-patterns-with/9781492052197/)
