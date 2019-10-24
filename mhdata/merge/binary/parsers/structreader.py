class StructReader:
    """Class used to read  mhw_armor_edit struct types, when a file contains multiple of them"""
    
    def __init__(self, data):
        self.offset = 0
        self.data = data

    def read_struct(self, struct_class):
        obj = struct_class(None, 0, self.data, offset=self.offset)
        self.offset += struct_class.STRUCT_SIZE
        return obj