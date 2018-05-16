from marshmallow import Schema, fields, ValidationError

def choice_check(*items):
    def validate_fn(check):
        if check not in items:
            item_str = ", ".join(items)
            raise ValidationError(f"Value {check} not one of ({item_str})")
    return validate_fn

def ValidatedStr(*items):
    return fields.Str(validate=choice_check(*items))

class ItemSchema(Schema):
    name = fields.Dict()
    description = fields.Dict()
    category = ValidatedStr("items", "material", "account", "ammo")
    rarity = fields.Int(allow_none=True, default=0)
    buy_price = fields.Int(allow_none=True)
    sell_price = fields.Int(allow_none=True)
    carry_limit = fields.Int(allow_none=True)

