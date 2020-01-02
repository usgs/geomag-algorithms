#! /bin/bash

export OPENID_METADATA_URL=https://code.usgs.gov/.well-known/openid-configuration
export OPENID_CLIENT_ID=...
export OPENID_CLIENT_SECRET=...
export SECRET_KEY=...
export SESSION_TYPE=sqlalchemy
export SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://user:password@127.0.0.1/dbname"
export SQLALCHEMY_TRACK_MODIFICATIONS=True

export FLASK_ENV=development
export FLASK_DEBUG=1
export FLASK_APP=geomagio.webservice


flask run
