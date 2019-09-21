# These are extra formats that were figured out separately from the main mhw_armor_edit repository.
# These are also public domain, feel free to use them however you wish.

from mhw_armor_edit.ftypes import StructField

class blist(StructField):
    def __init__(self, base, count):
        self.base = base
        self.count = count

    @property
    def size(self):
        return self.base.size * self.count
    
    def __get__(self, instance, owner):
        inner_offset = self.offset
        self.base.offset = inner_offset

        results = []
        for i in range(self.count):
            self.base.offset = inner_offset
            value = self.base.__get__(instance, owner)
            results.append(value)

            inner_offset += self.base.size

        return results