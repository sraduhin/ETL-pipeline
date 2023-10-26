from config.components.database import DATABASES

DB_CONNECT = {
    "dbname": DATABASES["default"]["NAME"],
    "user": DATABASES["default"]["USER"],
    "password": DATABASES["default"]["PASSWORD"],
    "host": DATABASES["default"]["HOST"],
    "port": DATABASES["default"]["PORT"],
    "options": DATABASES["default"]["OPTIONS"]["options"],
}
