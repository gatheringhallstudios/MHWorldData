# coding: utf-8
import logging
from collections import namedtuple

from mhw_armor_edit import ftypes as ft
from mhw_armor_edit.ftypes import (InvalidDataError, Struct)

log = logging.getLogger(__name__)


class GmdHeader(Struct):
    STRUCT_SIZE = 40
    magic: ft.uint()
    version: ft.uint()
    language: ft.uint()
    unk1: ft.uint()
    unk2: ft.uint()
    key_count: ft.uint()
    string_count: ft.uint()
    key_block_size: ft.uint()
    string_block_size: ft.uint()
    name_size: ft.uint()

    def __init__(self, parent, index, data, offset):
        super().__init__(parent, index, data, offset)
        self.name = self.read_name()

    def read_name(self):
        bstring = self.data[
                  GmdHeader.name_size.after
                  :GmdHeader.name_size.after + self.name_size]
        try:
            return bstring.decode("UTF-8")
        except Exception:
            return ""

    @property
    def total_size(self):
        return GmdHeader.name_size.after + self.name_size + 1


class GmdInfoItem(Struct):
    STRUCT_SIZE = 32
    string_index: ft.uint()
    hash_key_2x: ft.int()
    hash_key_3x: ft.int()
    pad: ft.pad(4)
    key_offset: ft.long()
    list_index: ft.long()


class GmdInfoItemKeyless:
    def __init__(self, parent, index):
        self.__dict__.update(parent)
        self.index = index
        self.string_index = index
        self.key_offset = -1

    def as_dict(self):
        return {
            key: getattr(self, key)
            for key in GmdInfoItem.fields()
        }

    def values(self):
        return tuple(
            getattr(self, key)
            for key in GmdInfoItem.fields()
        )


class GmdInfoTable:
    def __init__(self, data, offset, key_count, string_count):
        self.data = data
        self.offset = offset
        self.key_count = key_count
        self.string_count = string_count
        self.items = tuple(self._read_items(data))

    def _read_items(self, data):
        prev_string_index = 0
        for key_index in range(self.key_count):
            item = GmdInfoItem(
                self, key_index, data,
                self.offset + key_index * GmdInfoItem.STRUCT_SIZE)
            for missing_string_index in range(prev_string_index + 1, item.string_index):
                yield GmdInfoItemKeyless(item.as_dict(), missing_string_index)
            prev_string_index = item.string_index
            yield item
        for key_index in range(prev_string_index + 1, self.string_count):
            yield GmdInfoItemKeyless({}, key_index)

    @property
    def after(self):
        return self.offset + (self.key_count * GmdInfoItem.STRUCT_SIZE)

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, index):
        return self.items[index]


class GmdBucketItem(Struct):
    STRUCT_SIZE = 8
    unk1: ft.long()


class GmdBucketList:
    SIZE = 2048
    modified = False

    def __init__(self, parent, data, offset):
        self.parent = parent
        self.data = data
        self.offset = offset
        self.items = list(self._read_items())

    def _read_items(self):
        index = 0
        offset = self.offset
        while offset < self.offset + self.SIZE:
            item = GmdBucketItem(self, index, self.data, offset)
            offset = item.after
            index += 1
            yield item

    @property
    def after(self):
        return self.offset + self.SIZE


class GmdStringTable:
    def __init__(self, data, offset, block_size, count):
        self.data = data
        self.offset = offset
        self.block_size = block_size
        self.count = count
        self.items = self._read_items()
        if len(self.items) != self.count:
            raise InvalidDataError(
                f"expected {self.count} keys, read {len(self.items)}.")

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, key):
        if key == -1:
            return ""
        return self.items[key]

    def __len__(self):
        return len(self.items)

    @property
    def after(self):
        return self.offset + self.block_size

    def _read_items(self):
        return [
            it.decode("UTF-8")
            for it in self.data[self.offset:-1].split(b"\x00")
        ]


class GmdKeyTable(GmdStringTable):
    def _read_items(self):
        i = 0
        offset = 0
        items = {}
        val = bytearray()
        while i < self.block_size:
            ch = self.data[self.offset + i]
            i += 1
            if ch == 0:
                items[offset] = val.decode("UTF-8")
                val = bytearray()
                offset = i
            else:
                val.append(ch)
        return items


GmdItem = namedtuple("GmdItem", (
    "string_index",
    "key_offset",
    "key",
    "value",
    "hash_key_2x",
    "hash_key_3x",
    "pad",
    "list_index",
))


class Gmd:
    MAGIC = 0x00444d47
    modified = False  # GMDs are never modifiable

    def __init__(self, data):
        self.data = data
        self.header = GmdHeader(self, 0, data, 0)
        self.info_table = GmdInfoTable(data, self.header.total_size,
                                       self.header.key_count,
                                       self.header.string_count)
        self.unknown_block = GmdBucketList(self, data, self.info_table.after)
        self.key_table = GmdKeyTable(self.data,
                                     self.unknown_block.after,
                                     self.header.key_block_size,
                                     self.header.key_count)
        self.string_table = GmdStringTable(self.data,
                                           self.key_table.after,
                                           self.header.string_block_size,
                                           self.header.string_count)
        self.items = [
            GmdItem(
                key=self.key_table[info.key_offset],
                value=self.string_table[info.string_index],
                **info.as_dict())
            for info in self.info_table
        ]

    def get_string(self, index, default=None):
        try:
            value = self.string_table[index]
            # return f"{value}({index})"
            return value
        except IndexError:
            return default

    @classmethod
    def check_header(cls, data):
        header = GmdHeader(None, 0, data, 0)
        if header.magic != cls.MAGIC:
            raise InvalidDataError(
                f"magic byte invalid: expected {cls.MAGIC:04X}, found {header.magic:04X}")
        log.debug("key_count: %s, string_count: %s",
                  header.key_count,
                  header.string_count)

    @classmethod
    def load(cls, fp):
        data = bytearray(fp.read())
        cls.check_header(data)
        return cls(data)
