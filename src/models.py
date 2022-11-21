from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from src import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hash = db.Column(db.String(255), nullable=False)
    token_cookie = db.Column(db.String(255), nullable=True, default=None)
    #pictures = relationship('Picture', back_populates='user')

    def __repr__(self):
        return f"User({self.id}, {self.username}, {self.email})"


class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(120), nullable=False)
    birthday = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(100), nullable=True)
    phones = db.relationship('PhoneToContact', back_populates='contact')


class PhoneToContact(db.Model):
    __tablename__ = 'phones'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    phone = db.Column(db.String(100))
    contact_id = db.Column(ForeignKey('contacts.id', ondelete='CASCADE'), nullable=False)
    contact = db. relationship('Contact', back_populates='phones')


association_table = db.Table("association_table", db.Model.metadata,
    db.Column("note_id", ForeignKey("notes.id"), primary_key=True),
    db.Column("tag_id", ForeignKey("note_tags.id"), primary_key=True),
)


class NoteTag(db.Model):
    __tablename__ = 'note_tags'
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE'))
    notes = db.relationship('Note', secondary=association_table, back_populates='note_tags')


class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    note_text = db.Column(db.String(120), nullable=False)
    note_tags = relationship('NoteTag', secondary=association_table, back_populates='notes')
    user_id = db.Column(db.ForeignKey('users.id', ondelete='CASCADE'))

    def __repr__(self):
        if len(self.note_tags) > 0:
            return f'Tags: {[t.tag_name for t in self.note_tags]}\n{self.note_text}'
        return f'{self.note_text}'



class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key=True)
    news1 = db.Column(db.String(250), nullable=False)
    news2 = db.Column(db.String(250), nullable=False)
    news3 = db.Column(db.String(250), nullable=False)
    link1 = db.Column(db.String(250), nullable=False)
    link2 = db.Column(db.String(250), nullable=False)
    link3 = db.Column(db.String(250), nullable=False)


class Sport(db.Model):
    __tablename__ = 'sport'
    id = db.Column(db.Integer, primary_key=True)
    sport1 = db.Column(db.String(250), nullable=False)
    sport2 = db.Column(db.String(250), nullable=False)
    sport3 = db.Column(db.String(250), nullable=False)
    s_link1 = db.Column(db.String(250), nullable=False)
    s_link2 = db.Column(db.String(250), nullable=False)
    s_link3 = db.Column(db.String(250), nullable=False)


class Valute(db.Model):
    __tablename__ = 'valute'
    id = db.Column(db.Integer, primary_key=True)
    bank1_eur = db.Column(db.String(250), nullable=False)
    bank1_usd = db.Column(db.String(250), nullable=False)
    bank2_usd = db.Column(db.String(250), nullable=False)
    bank2_eur = db.Column(db.String(250), nullable=False)


class Weather(db.Model):
    __tablename__ = 'weather'
    id = db.Column(db.Integer, primary_key=True)
    gis1 = db.Column(db.String(250), nullable=False)
    gis2 = db.Column(db.String(250), nullable=False)
    gis3 = db.Column(db.String(250), nullable=False)
