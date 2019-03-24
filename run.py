from burn.server import app
import logging


logging.basicConfig(level=logging.DEBUG)

app.config["BURN_DATABASE_FILE"] = './burn.db'
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 10
app.config["BURN_MAX_STORAGE"] = 1024

if __name__ == "__main__":
    app.debug = True
    app.run(host = '0.0.0.0')
