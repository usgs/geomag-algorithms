from restricted_app import create_app

restricted_app = create_app()

if __name__ == "__main__":
    restricted_app.run(host="0.0.0.0")
