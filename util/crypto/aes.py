from hashlib import md5
from base64 import b64decode
from base64 import b64encode
from Crypto.Cipher import AES

# Padding for the input string --not
# related to encryption itself.
BLOCK_SIZE = 16  # Bytes


def pad(s):
    length = BLOCK_SIZE - (len(s) % BLOCK_SIZE)
    s += bytes([length]) * length
    return s


unpad = lambda s: s[:-ord(s[len(s) - 1:])]


class AESCipher:
    """
    Usage:
        c = AESCipher('password').encrypt('message')
        m = AESCipher('password').decrypt(c)
    Tested under Python 3 and PyCrypto 2.6.1.
    """

    def __init__(self, key):
        self.key = key.encode('utf8')

    def encrypt(self, raw):
        raw = pad(raw.encode('utf8'))
        cipher = AES.new(self.key, AES.MODE_ECB)
        return b64encode(cipher.encrypt(raw)).decode('utf8')

    def decrypt(self, enc):
        enc = b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_ECB)
        return unpad(cipher.decrypt(enc)).decode('utf8')

# pwd = '8NONwyJtHesysWpM'
# msg = 'ABCDEFGH'
# cipher_text = AESCipher(pwd).encrypt(msg)
# print('Ciphertext:', cipher_text)
# print('plaintext:', AESCipher(pwd).decrypt(cipher_text))
