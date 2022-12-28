# InstaSearch

This is a test application/assignment for a technical role that mocks the functionalities of the back-end of a very basic social media application.  
## Functionalities

* Registration: Users are made to register with an email address and a password.
* On-boarding: Users who have been authenticated successfully can now provide their details (username, follower_count and bio). These details can only be provided once per user.
* Search: The search functionality allows anyone (authenticated or not) to find influencers (users who have completed on-boarding) using certain attributes such as maximum number of followers, minimum number of followers and a keyword which matches an influencer whose username or bio contains this keyword

## Technologies
The app is built on Python(FastAPI) as that is what the test is based on, but if I was asked to build it again I certainly won't look elsewhere.
PostgreSQL is the choice for the Database.
Alembic is the tool used for DB migrations.
SQLAlchemy was used as the database driver (in conjunction with psycopg2)

## Authentication
Authentication of the app is done using JWT cookies. This was implemented using the fastapi-jwt-auth library.
Once a user is authenticated with the login route, cookies are assigned containing the access and refresh tokens.

All your files and folders are presented as a tree in the file explorer. You can switch from one to another by clicking a file in the tree.

## How to install the project
* Download/Clone the application source code
* Install Python
* Install the virtualenv library or any virtual environment manager on python
    ``pip install virtualenv``  
* Create a virtual environment in the project root after installation of virtualenv
    ``virtualenv env``
* Activate the newly created virtual environment, you can use this command on linux: 
    ``source env/bin/activate``
* By now your current working directory should be the project root, install the dependencies using the requirements file:
    ``pip install -r 'requirements.txt'``
 * Add a new environment variable file which will contain your database connection string:
    ``echo DB_URL = "<db_connection_string>" >> .env``
 You will also need some other environment variables:
 ACCESS_TOKEN_EXPIRES_IN: number (Amount of minutes before access token expires)
REFRESH_TOKEN_EXPIRES_IN: number (Amount of minutes before refresh token expires)
JWT_SECRET_KEY: string ( A secure string which will help with JWT orchestration)
* Use Alembic to migrate changes to the DB:
    ``alembic revision -m "Any name for migration"``
    ``alembic upgrade head``
* You can now run the project with: 
    ``uvicorn app.main:app --reload``

If you've completed the above steps, you are good to go with using the application.

## Usage
You can follow through with the [API collection](https://documenter.getpostman.com/view/17243864/2s8Z6yVXVh) to see the app usage.