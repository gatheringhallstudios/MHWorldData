from typing import Iterable
from pathlib import Path
from Crypto.Cipher import Blowfish

from .structs_ext import MibHeader, MibObjective, MibObjectiveHeader, MibObjectiveSection
from .structreader import StructReader
from ...binary.load import load_text

class QuestBinary:
    "An encapsulation of quest binary data"
    def __init__(
        self, 
        header: MibHeader, 
        objectives: Iterable[MibObjective], 
        sub_objectives: Iterable[MibObjective], 
        objective_section: MibObjectiveSection
    ):
        self.header = header
        self.objectives = objectives
        self.sub_objectives = sub_objectives
        self.objective_section = objective_section

def load_quest(filepath) -> QuestBinary:
    filepath = Path(filepath)

    data = CapcomBlowfish(open(filepath,'rb').read())

    reader = StructReader(data)

    header = reader.read_struct(MibHeader)

    objectives = []
    for i in range(2):
        obj = reader.read_struct(MibObjective)
        objectives.append(obj)

    objective_header = reader.read_struct(MibObjectiveHeader)

    sub_objectives = []
    for i in range(2):
        obj = reader.read_struct(MibObjective)
        sub_objectives.append(obj)

    objective = reader.read_struct(MibObjectiveSection)

    return QuestBinary(header, objectives, sub_objectives, objective)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def endianness_reversal(data):
    return b''.join(map(lambda x: x[::-1],chunks(data, 4)))

def CapcomBlowfish(file):
    cipher = Blowfish.new(b"TZNgJfzyD2WKiuV4SglmI6oN5jP2hhRJcBwzUooyfIUTM4ptDYGjuRTP", Blowfish.MODE_ECB)
    return endianness_reversal(cipher.decrypt(endianness_reversal(file)))
