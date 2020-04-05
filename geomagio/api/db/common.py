"""
Define the database connection and sqlalchemy metadata objects.


Configuration:
    uses environment variables:

    DATABASE_URL  - url to connect to database.
                    Default is "sqlite:///./api_database.db"


Database models:

    Register with metadata.

        class DatabaseModel(orm.Model):
            __database__ = database
            __metadata__ = sqlalchemy_metadata

    And import in create.py, so scripts can manage the database schema.


Applications must manage the database connections:

    @app.on_event("startup")
    async def on_startup():
        await database.connect()


    @app.on_event("shutdown")
    async def on_shutdown():
        await database.disconnect()
"""

import os

from databases import Database
from sqlalchemy import MetaData


# database connection
database = Database(os.getenv("DATABASE_URL", "sqlite:///./api_database.db"))

# metadata used to manage database schema
sqlalchemy_metadata = MetaData()
