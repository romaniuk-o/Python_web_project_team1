from flask import render_template, request, flash, redirect, url_for, session, make_response
from werkzeug.utils import secure_filename
import pathlib
import uuid
from datetime import datetime, timedelta
from marshmallow import ValidationError

from . import app





@app.route('/healthcheck')
def healthcheck():
    return 'I am a finaly project, team 1'


@app.route('/', strict_slashes=False)
def index():
    auth = True if 'username' in session else False
    return render_template('pages/index.html', title='Final project, TEAM 1', auth=auth)




































