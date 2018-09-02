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

class NullableBool(fields.Boolean):
    """
    Defines a boolean that serializes null to false so long as null_is_false is passed
    Created because allow_none early exits deserialization'''
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.null_is_false = kwargs.get('null_is_false', False)

    def deserialize(self, value, attr=None, data=None):
        if self.null_is_false and value is None:
            return False
        return super().deserialize(value, attr, data)

    def _serialize(self, value, attr, obj):
        if self.null_is_false and value is False:
            return None
        return super()._serialize(value, attr, obj)

class ExcelBool(NullableBool):
    def _serialize(self, value, attr, obj):
        if value == True:
            return 'TRUE'
        elif self.null_is_false:
            return None
        else:
            return 'FALSE'
