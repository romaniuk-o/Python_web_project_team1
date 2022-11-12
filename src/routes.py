from flask import render_template, request, flash, redirect, url_for, session, make_response
from werkzeug.utils import secure_filename
import pathlib
import uuid
from datetime import datetime, timedelta
from marshmallow import ValidationError

from . import app
from src.libs.validation_file import phone_valid
from src.repository import contact_methods
from src.libs.validation_schemas import NewContactSchema


@app.route('/healthcheck')
def healthcheck():
    return 'I am a finaly project, team 1'


@app.route('/', strict_slashes=False)
def index():
    auth = True if 'username' in session else False
    return render_template('pages/index.html', title='Final project, TEAM 1', auth=auth)


@app.route('/new_contact', methods=['GET', 'POST'], strict_slashes=False)
def new_contact():
    if request.method == 'POST':
        try:
            NewContactSchema().load(request.form)
        except ValidationError as err:
            return render_template('pages/new_contact.html', messages=err.messages)
        name = request.form.get('name')
        phone = request.form.get('phone')
        birthday = request.form.get('birthday')
        address = request.form.get('address')
        email = request.form.get('email')
        if phone_valid(phone) is None:
            flash(f'Phone number is incorect\n'
                  f'Phone number must be 12 digits, and start with 380')
            return render_template('pages/new_contact.html')
        contact_methods.add_new_contact(name, phone_valid(phone), birthday, address, email)

        flash('added successfully')
    return render_template('pages/new_contact.html')


@app.route('/show_address_book', methods=['GET', 'POST'], strict_slashes=False)
def show_address_book():
    if request.method == 'GET':
        contacts = contact_methods.show_address_book()
        phones = contact_methods.show_phones_for_contact()
    return render_template('pages/show_address_book.html', contacts=contacts, phones=phones)


@app.route('/show_address_book/delete/<c_id>', methods=['GET', 'POST'], strict_slashes=False)
def delete_address_book(c_id):
    if request.method == 'GET':
        contact_methods.delete_contact(c_id)
        contact_methods.delete_contact_phones(c_id)
        flash('Deleted successfully!')
    return redirect(url_for('show_address_book'))


@app.route('/show_address_book/edit/<c_id>', methods=['GET', 'POST'], strict_slashes=False)
def edit_address_book(c_id):
    contact = contact_methods.get_contact(c_id)
    phones = contact_methods.get_contacts_phones(c_id)
    if request.method == 'POST':
        name = request.form.get('name')
        birthday = request.form.get('birthday')
        address = request.form.get('address')
        email = request.form.get('email')
        contact_methods.edit_contact(c_id, name, birthday, address, email)
        flash('Changed successfully!')
        return redirect(url_for('result_address_book'))
    return render_template('pages/edit_address_book.html', contact=contact, phones=phones)


@app.route('/find_address_book', methods=['GET', 'POST'], strict_slashes=False)
def find_address_book():
    if request.method == 'POST':
        symbol = request.form.get('symbol')
        contact = contact_methods.find_notate(symbol)
        return render_template('pages/result_address_book.html', contact=contact)
    return render_template('pages/find_address_book.html')


@app.route('/add_new_phone', methods=['GET', 'POST'], strict_slashes=False)
def add_new_phone():
    if request.method == 'POST':
        contact_id = request.form.get('user_id')
        phone = request.form.get('phone')
        if phone_valid(phone) is None:
            flash(f'Phone number is incorect\n'
                  f'Phone number must be 12 digits, and start with 380')
            return render_template('pages/add_new_phone.html')
        try:
            contact_methods.add_new_phone(contact_id, phone)
        except ValueError:
            flash('Phone already exist')
            return render_template('pages/add_new_phone.html')

        flash('added successfully')
    return render_template('pages/add_new_phone.html')

































