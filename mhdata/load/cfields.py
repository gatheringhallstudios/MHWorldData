"""
Custom fields used by the marshmallow schema
"""

from marshmallow import fields, ValidationError


def choice_check(*items):
    def validate_fn(check):
        if check not in items:
            item_str = ", ".join(map(lambda i: i or "None", items))
            raise ValidationError(f"Value {check} not one of ({item_str})")
    return validate_fn


def ValidatedStr(*items):
    return fields.Str(allow_none=True, validate=choice_check(*items))

class EmptyBool(fields.Boolean):
    '''A subclass of fields.Boolean, that deserializes None to false.
    Created because allow_none early exits deserialization'''
    def deserialize(self, value, attr=None, data=None):
        if value is None:
            return False
        return super().deserialize(value, attr, data)
