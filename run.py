from burn.server import app

app.config["BURN_DATABASE_FILE"] = '/dev/shm/tmp123-burn.db'
app.config["BURN_MAX_MESSAGE_LENGTH"] = 512
app.config["BURN_MAX_STORAGE"] = 1024

if __name__ == "__main__":
    app.debug = True
    app.run(host = '0.0.0.0')
