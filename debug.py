from burn.server import app
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app.debug = True
    app.run(host='0.0.0.0')
