import os.path
from sqlalchemy.exc import IntegrityError
from flask import render_template, request, flash, redirect, url_for, session, make_response, send_from_directory
from werkzeug.utils import secure_filename

import pathlib
import uuid
from datetime import datetime, timedelta
from marshmallow import ValidationError
from . import app
from src.libs.validation_file import phone_valid
from src.repository import contact_methods, regist
from src.libs.validation_schemas import NewContactSchema
from src.libs.validation_schemas import RegistrationSchema, LoginSchema
from src.repository.files import allowed_file
from src import db
from .models import Note, NoteTag, User





@app.before_request
def before_func():
    auth = True if 'username' in session else False
    if not auth:
        token_user = request.cookies.get('username')
        if token_user:
            user = regist.get_user_by_token(token_user)
            if user:
                session['username'] = {"username": user.username, "id": user.id}



@app.route('/healthcheck')
def healthcheck():
    return 'I am a finally project, team 1'



@app.route('/', strict_slashes=False)
def index():
    auth = True if 'username' in session else False
    if auth:
        user_name = session['username']['username']
    else:
        user_name = ''
    return render_template('pages/index.html', title='Final project, TEAM 1', auth=auth, user_name=user_name)



@app.route('/new_contact', methods=['GET', 'POST'], strict_slashes=False)
def new_contact():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    user_name = session['username']['username']
    user_id = session['username']['id']
    if request.method == 'POST':
        try:
            NewContactSchema().load(request.form)
        except ValidationError as err:
            return render_template('pages/new_contact.html', messages=err.messages, user_name=user_name, auth=auth)
        name = request.form.get('name')
        phone = request.form.get('phone')
        birthday = request.form.get('birthday')
        address = request.form.get('address')
        email = request.form.get('email')
        if phone_valid(phone) is None:
            flash(f'Phone number is incorrect\n'
                  f'Phone number must be 12 digits, and start with 380')
            return render_template('pages/new_contact.html', user_name=user_name, auth=auth)
        try:
            print(contact_methods.add_new_contact(name, phone_valid(phone), birthday, address, email, user_id))
        except IntegrityError as err:
            print(f'this{err}')
            flash('this email or phone number isn\'t unique')
            return render_template('pages/new_contact.html', user_name=user_name, auth=auth)
        flash('added successfully')
    return render_template('pages/new_contact.html', user_name=user_name, auth=auth)


@app.route('/show_address_book', methods=['GET', 'POST'], strict_slashes=False)
def show_address_book():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    user_name = session['username']['username']
    user_id = session['username']['id']
    if request.method == 'GET':
        contacts = contact_methods.show_address_book(user_id)
        phones = contact_methods.show_phones_for_contact(user_id)
    return render_template('pages/show_address_book.html', contacts=contacts, phones=phones, user_name=user_name, auth=auth)


@app.route('/show_address_book/delete/<c_id>', methods=['GET', 'POST'], strict_slashes=False)
def delete_address_book(c_id):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    if request.method == 'GET':
        contact_methods.delete_contact(c_id)
        contact_methods.delete_contact_phones(c_id)
        flash('Deleted successfully!')
    return redirect(url_for('show_address_book'))


@app.route('/show_address_book/edit/<c_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_address_book(c_id):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    user_name = session['username']['username']
    contact = contact_methods.get_contact(c_id)
    phones = contact_methods.get_contacts_phones(c_id)
    if request.method == 'POST':
        try:
            NewContactSchema().load(request.form)
        except ValidationError as err:
            flash(f'{err}')
            return render_template('pages/edit_address_book.html', contact=contact, phones=phones, user_name=user_name, auth=auth, messages=err.messages)
        name = request.form.get('name')
        birthday = request.form.get('birthday')
        address = request.form.get('address')
        email = request.form.get('email')
        phones = request.form.getlist('phone')
        for p in phones:
            if phone_valid(p) != None :
                contact_methods.edit_contact(c_id, name, birthday, address, email)
                contact_methods.edit_phones(c_id, phones)
                flash('Changed successfully!')
            else:
                flash('Incorrect phone number!')
                return redirect(request.url)
            return redirect(url_for('show_address_book'))
    return render_template('pages/edit_address_book.html', contact=contact, phones=phones, user_name=user_name, auth=auth)


@app.route('/find_address_book', methods=['GET', 'POST'], strict_slashes=False)
def find_address_book():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    user_name = session['username']['username']
    user_id = session['username']['id']
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        contacts, phones = contact_methods.find_address_book(symbol, user_id)
        print(contacts, phones)
        return render_template('pages/result_address_book.html', contacts=contacts,
                               phones=phones, user_name=user_name, auth=auth, user_id=user_id)
    return render_template('pages/find_address_book.html', user_name=user_name, auth=auth)


@app.route('/show_address_book/add_new_phone/<c_id>', methods=['GET', 'POST'], strict_slashes=False)
def add_new_phone(c_id):
    print(f'first {c_id}')
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    user_name = session['username']['username']
    user_id = session['username']['id']
    if request.method == 'POST':
        print(c_id)
        phone = request.form.get('phone')
        if phone_valid(phone) is None:
            flash(f'Phone number is incorect\n'
                  f'Phone number must be 12 digits, and start with 380')
            return redirect(url_for('show_address_book'))
        try:
            contact_methods.add_new_phone(c_id, phone, user_id)
        except ValueError:
            flash('Phone already exist')
            return redirect(request.url)
        flash('added successfully')
        return redirect(url_for('show_address_book'))

    return render_template('pages/add_new_phone.html', user_name=user_name, auth=auth, cont_id=c_id)


@app.route('/notes', methods=['GET', 'POST'], strict_slashes=False)
def notes_main():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    user_name = session['username']['username']
    tags = db.session.query(NoteTag).filter(NoteTag.user_id == session['username']['id']).all()
    # tags = db.session.query(NoteTag).filter(NoteTag.user_id == 1).all()  # for testing
    notes = []
    if 'username' in session:
        notes = db.session.query(Note).filter(User.id == session['username']['id']).all()
    # notes = db.session.query(Note).filter(Note.user_id == 1).all()  # for testing
    if request.method == 'GET':
        return render_template('pages/notes_main.html', notes=notes, tags=tags, auth=auth, user_name=user_name)
    if request.method == 'POST':
        filter_tag = request.form.get('filter_tag')
        search_text = request.form.get('search_text')
        if filter_tag and request.form['btn'] == 'set_filter':
            notes_by_tag = []
            for note in notes:
                if int(filter_tag) in [t.id for t in note.note_tags]:
                    notes_by_tag.append(note)
            return render_template('pages/notes_main.html', notes=notes_by_tag, tags=tags, auth=auth, user_name=user_name)
        if request.form['btn'] == 'clear_filter':
            return render_template('pages/notes_main.html', notes=notes, tags=tags, auth=auth, user_name=user_name)
        if search_text and request.form['btn'] == 'search':
            notes_by_search = []
            for note in notes:
                if [t.tag_name for t in note.note_tags if search_text in t.tag_name] or (search_text in note.note_text):
                    print([t.tag_name for t in note.note_tags if search_text in t.tag_name], [t.tag_name for t in note.note_tags if search_text in t.tag_name] is True)
                    notes_by_search.append(note)
            return render_template('pages/notes_main.html', notes=notes_by_search, tags=tags, auth=auth, user_name=user_name)


@app.route('/notes/tags', methods=['GET', 'POST'], strict_slashes=False)
def add_tags():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    user_name = session['username']['username']
    tags = []
    if 'username' in session:
        tags = db.session.query(NoteTag).filter(NoteTag.user_id == session['username']['id']).all()
    # tags = db.session.query(NoteTag).filter(NoteTag.user_id == 1).all()  # for testing
    if request.method == 'POST':
        tag_name = request.form.get('tag_name')
        tag = NoteTag(tag_name=tag_name, user_id=session['username']['id'])
        # tag = NoteTag(tag_name=tag_name, user_id=1) #for testing
        user_tags = db.session.query(NoteTag).filter(NoteTag.user_id == session['username']['id']).all()
        if tag.tag_name in [t.tag_name for t in user_tags]:
            flash('tag already there')
            return render_template('pages/tags.html', tags=tags, auth=auth, user_name=user_name)
        db.session.add(tag)
        db.session.commit()
        flash('Tag saved!')
        return redirect(url_for('add_tags'))
    return render_template('pages/tags.html', tags=tags, auth=auth, user_name=user_name)


@app.route('/notes/add', methods=['GET', 'POST'], strict_slashes=False)
def add_notes():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    user_name = session['username']['username']
    if request.method == 'POST':
        note_tags = request.form.getlist('tags')
        note_text = request.form.get('note_text')
        if len(note_text) == 0:
            flash('Please, enter note')
            return redirect(request.url)
        note = Note(note_text=note_text, user_id=session['username']['id'])
        choice_tags = db.session.query(NoteTag).filter(NoteTag.id.in_(note_tags), NoteTag.user_id == session['username']['id']).all()
        # note = Note(note_text=note_text, user_id=1) #for testing
        # choice_tags = db.session.query(NoteTag).filter(NoteTag.id.in_(note_tags), NoteTag.user_id == 1).all() #for testing
        for tag in choice_tags:
            note.note_tags.append(tag)
        db.session.add(note)
        db.session.commit()
        flash('Note saved!')
        return redirect(url_for('notes_main'))
    tags = []
    if 'username' in session:
        tags = db.session.query(NoteTag).filter(NoteTag.user_id == session['username']['id']).all()
    # tags = db.session.query(NoteTag).filter(NoteTag.user_id == 1).all() #for testing
    return render_template('pages/notes_add.html', tags=tags, auth=auth, user_name=user_name)


@app.route('/notes/delete/<note_id>', methods=['POST'], strict_slashes=False)
def note_delete(note_id):
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    if request.method == 'POST':
        db.session.query(Note).filter(Note.user_id == session['username']['id'], Note.id == note_id).delete()
        # db.session.query(Note).filter(Note.user_id == 1, Note.id == note_id).delete() #for testing
        db.session.commit()
        flash('Note deleted!')
    return redirect(url_for('notes_main'))


@app.route('/registration', methods=['GET', 'POST'], strict_slashes=False)
def registration():
    auth = True if 'username' in session else False
    if request.method == 'POST':
        try:
            RegistrationSchema().load(request.form)
        except ValidationError as err:
            return render_template('pages/registration.html', messages=err.messages)
        except IntegrityError as err:
            return render_template('pages/registration.html', messages=err)
        email = request.form.get('email')
        password = request.form.get('password')
        nick = request.form.get('nickname')
        print(email, password, nick)
        user = regist.create_user(email, password, nick)
        return redirect(url_for('sign_in'))
    if auth:
        return redirect(url_for('index'))
    else:
        return render_template('pages/registration.html')


@app.route('/sign_in', methods=['GET', 'POST'], strict_slashes=False)
def sign_in():
    auth = True if 'username' in session else False
    if request.method == 'POST':
        try:
            LoginSchema().load(request.form)
        except ValidationError as err:
            return render_template('pages/sign_in.html', messages=err.messages)

        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') == 'on' else False

        user = regist.login(email, password)
        if user is None:
            return redirect(url_for('sign_in'))
        session['username'] = {"username": user.username, "id": user.id}
        response = make_response(redirect(url_for('index')))
        if remember:
            # Треба створить token, та покласти його в cookie та БД
            token = str(uuid.uuid4())
            expire_data = datetime.now() + timedelta(days=60)
            response.set_cookie('username', token, expires=expire_data)
            regist.set_token(user, token)

        return response
    if auth:
        return redirect(url_for('index'))
    else:
        return render_template('pages/sign_in.html')


@app.route('/sign_out', strict_slashes=False)
def logout():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(url_for('index'))
    session.pop('username')
    response = make_response(redirect(url_for('index')))
    response.set_cookie('username', '', expires=-1)

    return response

@app.route('/files/upload', methods=['GET', 'POST'], strict_slashes=False)
def upload_file():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    user_name = session['username']['username']

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = pathlib.Path(app.config['UPLOAD_FOLDER']) / user_name
            save_path.mkdir(exist_ok=True, parents=True)
            file.save(save_path / filename)
            flash('File uploaded successfully')
            return redirect(url_for('upload_file'))
    return render_template('pages/upload.html', auth=auth, user_name=user_name)

@app.route('/uploads/<filename>')
def upload(filename):
    user_name = session['username']['username']
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], user_name), filename)

@app.route('/files', methods=['GET', 'POST'], strict_slashes=False)
def files_list():
    auth = True if 'username' in session else False
    if not auth:
        return redirect(request.url)
    user_name = session['username']['username']
    if request.method == 'POST':
        type_file = request.form.get('filter_type')
        dir_path = pathlib.Path(app.config['UPLOAD_FOLDER']) / user_name
        dir_path.mkdir(exist_ok=True, parents=True)
        files = []
        for file in dir_path.glob(f'*.{type_file}'):
            files.append(file.name)
        return render_template('pages/files.html', files=files, filetype=app.config['ALLOWED_EXTENSIONS'], auth=auth, user_name=user_name)
    return render_template('pages/files.html', filetype=app.config['ALLOWED_EXTENSIONS'], auth=auth, user_name=user_name)

@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    user_name = session['username']['username']
    file_path = pathlib.Path(app.config['UPLOAD_FOLDER']) / user_name / filename
    if file_path.exists():
        file_path.unlink()
    return redirect(url_for('files_list'))
