"""
File used to decrypt certain files. 
Decryption scheme was learned from the open source QuestDataDump project.
"""

from Crypto.Cipher import Blowfish

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def endianness_reversal(data):
    return b''.join(map(lambda x: x[::-1],chunks(data, 4)))

def CapcomBlowfish(data, key):
    cipher = Blowfish.new(key, Blowfish.MODE_ECB)
    return endianness_reversal(cipher.decrypt(endianness_reversal(data)))
