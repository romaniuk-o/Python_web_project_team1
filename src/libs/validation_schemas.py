from marshmallow import Schema, fields, validate


class NewContactSchema(Schema):
    name = fields.Str(validate=validate.Length(min=3), required=True)
    phone = fields.Str(required=True)
    birthday = fields.Str(required=False)
    address = fields.Str(required=False)
    email = fields.Str(required=False)



