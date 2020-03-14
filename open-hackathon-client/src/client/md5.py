# -*- coding: utf-8 -*-
"""
This file is covered by the LICENSING file in the root of this project.
"""

import hashlib
import sys

sys.path.append("..")

from client import app


def encode(plaintext):
    m = hashlib.md5()
    origin = plaintext + app.config['SECRET_KEY']
    m.update(origin.encode('utf8'))
    return m.hexdigest()


if __name__ == "__main__":
    print(encode("admin"))
