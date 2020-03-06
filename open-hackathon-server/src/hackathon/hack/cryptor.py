# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random
from urllib.request import urlopen
import os

from hackathon import Component

__all__ = ["Cryptor"]


class Cryptor(Component):
    """
    Encrypt and Decrypt files.
    """

    def __init__(self):
        """
        """
        self.password = "123456"

    def __derive_key_and_iv(self, salt, key_length, iv_length):
        d = d_i = ''
        while len(d) < key_length + iv_length:
            d_i = md5(d_i + self.password + salt).digest()
            d += d_i
        return d[:key_length], d[key_length:key_length + iv_length]

    def encrypt(self, in_file_name, out_file_name, key_length=32):
        """
        Encrypt the plaintext into the ciphertext

        :type in_file_name: str|unicode
        :param in_file_name: the plaintext file path. Example-/home/ubuntu/plaintext.txt
        :param out_file_name: the path where ciphertext file will be stored. Example-/home/ubuntu/ciphertext.txt
        :param key_length: key length. Example-32
        :return:
        """
        try:
            in_file = open(in_file_name, 'rb')
            out_file = open(out_file_name, 'wb')
            bs = AES.block_size
            salt = Random.new().read(bs - len('Salted__'))
            key, iv = self.__derive_key_and_iv(salt, key_length, bs)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            out_file.write('Salted__' + salt)
            finished = False
            while not finished:
                chunk = in_file.read(1024 * bs)
                if len(chunk) == 0 or len(chunk) % bs != 0:
                    padding_length = (bs - len(chunk) % bs) or bs
                    chunk += padding_length * chr(padding_length)
                    finished = True
                out_file.write(cipher.encrypt(chunk))
            in_file.close()
            out_file.close()
            self.log.debug("Encrypt %s to %s" % (in_file_name, out_file_name))
        except Exception:
            self.log.error("Failed to encrypt %s" % in_file_name)

    def decrypt(self, in_file_name, out_file_name, key_length=32):
        """
        Decrypt the plaintext into the ciphertext
        :param in_file_name: the ciphertext file path. Example-/home/ubuntu/ciphertext.txt
        :param out_file_name: the path where plaintext file will be stored. Example-/home/ubuntu/plaintext.txt
        :param key_length: Example-32
        :return:
        """
        try:
            in_file = open(in_file_name, 'rb')
            out_file = open(out_file_name, 'wb')
            bs = AES.block_size
            salt = in_file.read(bs)[len('Salted__'):]
            key, iv = self.__derive_key_and_iv(salt, key_length, bs)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            next_chunk = ''
            finished = False
            while not finished:
                chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
                if len(next_chunk) == 0:
                    padding_length = ord(chunk[-1])
                    chunk = chunk[:-padding_length]
                    finished = True
                out_file.write(chunk)
            in_file.close()
            out_file.close()
            self.log.debug("Decrypt %s to %s" % (in_file_name, out_file_name))
        except Exception:
            self.log.error("Failed to decrypt %s" % in_file_name)

    def recover_local_file(self, remote_url, local_url):
        """
        Recover the ciphertext from a server into plaintext
        :param remote_url: the ciphertext file url. Example-localhost:5000/static/upload/ciphertext
        :param local_url: the path where plaintext file will be stored
        :return:
        """
        try:
            remote_pem = urlopen(remote_url)
            encrypted_pem_file = open(local_url + ".encrypted", 'wb')
            encrypted_pem_file.write(remote_pem.read())
            encrypted_pem_file.close()
            self.decrypt(encrypted_pem_file.name, local_url)
            os.remove(encrypted_pem_file.name)
        except Exception:
            self.log.error("Failed to recover local file %s from server %s" % (local_url, remote_url))
