from marshmallow import Schema, fields, validate


class NewContactSchema(Schema):
    name = fields.Str(validate=validate.Length(min=3), required=True)
    phone = fields.Str(required=False)
    birthday = fields.Date(required=False)
    address = fields.Str(required=False)
    email = fields.Email(required=False, unique=True)


class RegistrationSchema(Schema):
    nickname = fields.Str(validate=validate.Length(min=3), required=True)
    email = fields.Email(required=True)
    password = fields.Str(validate=validate.Length(min=6), required=True)


class LoginSchema(Schema):
    remember = fields.Str()
    email = fields.Email(required=True)
    password = fields.Str(validate=validate.Length(min=6), required=True)



