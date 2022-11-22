import pathlib
from dotenv import dotenv_values
BASE_DIR = pathlib.Path(__file__).parent.parent
FILE_FOLDER = BASE_DIR / 'data' / 'files'
FILE_FOLDER.mkdir(parents=True, exist_ok=True)
config = dotenv_values(".env")


class Config:
    UPLOAD_FOLDER = str(FILE_FOLDER)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(BASE_DIR / 'data' / 'Python_web_team1.sqlite3')
    SECRET_KEY = config['SECRET_KEY']
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'xlsx'}
    MAX_CONTENT_LENGTH = 16 * 1000 * 1000
