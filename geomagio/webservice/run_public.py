from __future__ import absolute_import
from public_app import create_app

public_app = create_app()

if __name__ == "__main__":
    public_app.run(host="0.0.0.0")
