from flask_sqlalchemy import SQLAlchemy
from api.logger import LogSetup
from flask_migrate import Migrate


db = SQLAlchemy()
logs = LogSetup()
migrate = Migrate()
