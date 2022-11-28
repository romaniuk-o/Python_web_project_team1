from _sqlite3 import IntegrityError
from sqlalchemy import or_


from src import db
from src import models
from src.libs.validation_file import phone_valid


def add_new_contact(name, phone, birthday, address, email, user_id):
    try:
        new_contact = models.Contact(user_name=name, email=email, birthday=birthday, address=address, user_id=user_id)
        db.session.add(new_contact)
        db.session.commit()
        phone = models.PhoneToContact(phone=phone, contact_id=new_contact.id, user_id=user_id)
        db.session.add(phone)
        db.session.commit()
    except IntegrityError as err:
        return err


def show_address_book(user_id):
    return db.session.query(models.Contact).filter(models.Contact.user_id == user_id).all()


def show_phones_for_contact(user_id):
    return db.session.query(models.PhoneToContact).filter(models.Contact.user_id==user_id).all()


def delete_contact(c_id):
    contact = db.session.query(models.Contact).filter(models.Contact.id==c_id).delete()
    db.session.commit()


def delete_contact_phones(n_id):
    contact = db.session.query(models.PhoneToContact).filter(models.PhoneToContact.contact_id==n_id).delete()
    db.session.commit()


def get_contact(c_id):
    return db.session.query(models.Contact).filter(models.Contact.id == c_id).one()


def get_contacts_phones(c_id):
    return db.session.query(models.PhoneToContact).filter(models.PhoneToContact.contact_id == c_id).all()


def edit_contact(c_id, name, birthday, address, email):
    c = db.session.query(models.Contact).filter(models.Contact.id == c_id).first()
    c.user_name = name
    c.birthday = birthday
    c.address = address
    c.email = email
    db.session.commit()


def edit_phones(c_id, phones_from_html):
    for phone_html in phones_from_html:
        if phone_html != '' and phone_valid(phone_html) == None:
            raise ValueError
        else:
            phones = db.session.query(models.PhoneToContact).filter(models.PhoneToContact.contact_id == c_id).all()
            i = 0
            for phone in phones:
                if phones_from_html[i] == '':
                    phone_ = db.session.query(models.PhoneToContact).filter(models.PhoneToContact.id == phone.id).delete()
                    db.session.commit()
                else:
                    phone.phone = phones_from_html[i]
                    db.session.commit()
                    i +=1


def add_new_phone(contact_id, phone, user_id):
    phones = db.session.query(models.PhoneToContact).all()
    for ph in phones:
        if ph.phone == phone_valid(phone):
            raise ValueError
    new_phone = models.PhoneToContact(contact_id=contact_id, phone=phone, user_id=user_id)
    db.session.add(new_phone)
    db.session.commit()
    return f'new phone added'


def find_address_book(symb, user_id):
    phones_symb = db.session.query(models.PhoneToContact).filter(models.PhoneToContact.phone.like(f'%{symb}%')).all()
    contacts_symb = db.session.query(models.Contact).filter(or_(models.Contact.user_name.like(f'%{symb}%'),
                                                     models.Contact.address.like(f'%{symb}%'),
                                                     models.Contact.birthday.like(f'%{symb}%'),
                                                     models.Contact.email.like(f'%{symb}%')), models.Contact.user_id==user_id ).all()

    contacts_symb_new = db.session.query(models.Contact, models.PhoneToContact).\
                                    add_columns(models.Contact.id,
                                    models.Contact.user_name,
                                    models.Contact.address,
                                    models.Contact.birthday,
                                    models.Contact.email,
                                    models.PhoneToContact.phone).filter(
                                    models.Contact.id == models.PhoneToContact.contact_id).filter(
                                    or_(models.Contact.user_name.like(f'%{symb}%'),
                                        models.Contact.address.like(f'%{symb}%'),
                                        models.Contact.birthday.like(f'%{symb}%'),
                                        models.Contact.email.like(f'%{symb}%'),
                                        models.PhoneToContact.phone.like(f'%{symb}%')), models.Contact.user_id == user_id).all()
    new_cont_list = []
    for cont in contacts_symb_new:
        new_cont_list.append(cont.id)
    bb = set(new_cont_list)
    c = []
    p = []
    for i in bb:
        c_ = db.session.query(models.Contact).filter(models.Contact.id == i).first()
        c.append(c_)
    p = db.session.query(models.PhoneToContact).all()

    # phones = db.session.query(models.PhoneToContact).filter(models.PhoneToContact.contact_id==i.id for i in contact_list).all()
    return c, p