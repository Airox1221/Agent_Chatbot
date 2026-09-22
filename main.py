import uvicorn
import configparser

if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("config.ini")

    host = config["server"]["host"]
    port = config["server"].getint("port")
    reload = config["server"].getboolean("reload")


    uvicorn.run(
        "app.server.api:app",
        host=host,
        port=port,
        reload=reload
    )