"""
Custom fields used by the marshmallow schema
"""

import collections
from marshmallow import fields, ValidationError, Schema, pre_load, post_dump

from mhdata.util import group_fields, ungroup_fields
from mhdata import cfg

def choice_check(*items):
    def validate_fn(check):
        if check not in items:
            item_str = ", ".join(map(lambda i: i or "None", items))
            raise ValidationError(f"Value {check} not one of ({item_str})")
    return validate_fn


def ValidatedStr(*items, **kwargs):
    return fields.Str(allow_none=True, validate=choice_check(*items), **kwargs)

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

class NestedPrefix(fields.Nested):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **{ 'many': False, **kwargs })
        self.prefix = kwargs.get('prefix', None)

class BaseSchema(Schema):
    "Base class for all schemas in this project"
    __groups__ = ()
    __translation_groups__ = ()
    class Meta:
        ordered = True

    def identify_prefixes(self):
        "Identifies all potential prefixes by examining the fields"
        # note: could be made more efficient via caching? See if there is a way to dirty check fields
        prefixes = []
        for name, field in self.fields.items():
            if isinstance(field, NestedPrefix):
                prefixes.append(field.prefix or name)
        return prefixes

    @pre_load
    def group_fields(self, data):
        if not isinstance(data, collections.Mapping):
            raise TypeError("Invalid data type, perhaps you forgot many=true?")
        groups = (list(self.__groups__ or [])
                    + list(self.__translation_groups__ or [])
                    + self.identify_prefixes())
        return group_fields(data, groups=groups)

    @post_dump
    def ungroup_fields(self, data):
        groups = list(self.__groups__ or []) + self.identify_prefixes()
        result = ungroup_fields(data, groups=groups)

        # Now weave the translation fields at the end
        translation_groups = list(self.__translation_groups__ or [])
        for lang in cfg.all_languages:
            for field in translation_groups:
                try:
                    field_value = result[field]
                except KeyError:
                    raise KeyError(f'No schema entry for {field}. If the field is exported separately, use __groups__ instead')
                
                try:
                    result[f"{field}_{lang}"] = field_value[lang]
                except KeyError:
                    raise KeyError(f'No language entry {lang} for field {field}')
        for field in translation_groups:
            del result[field]
                
        return result
