"""
This module provides an abstract interface allowing the creation 
and verification of cryptographically strong hashes.
"""

__all__ = ['hash_secret', 'verify_secret']

import os

import sqldb

from argon2 import low_level
from argon2.low_level import hash_secret_raw, Type
from typing import Tuple


CRYPTO_PARAMS = {
    'time_cost': 2,
    'memory_cost': 102400,
    'parallelism': 8,
    'hash_len': sqldb.HASH_LEN,
    'type': Type.ID,
}

SECRET_ENCODING = 'utf8'


def hash_secret(secret: str) -> Tuple[bytes, bytes]:
    """
    Hashes the given secret (a utf8 string), returning a tuple of the 
    derived hash and the newly-generated salt used.
    """
    secret_bytes = secret.encode(SECRET_ENCODING)
    secret_salt = os.urandom(sqldb.HASH_LEN)
    secret_hash = hash_secret_raw(secret_bytes, secret_salt, **CRYPTO_PARAMS)

    return secret_hash, secret_salt


def verify_secret(secret: str, salt: bytes, known_hash: bytes) -> bool:
    """
    Checks whether the given secret (a utf8 string) hashes (using the 
    given salt) to the given known hash. Returns whether the hashes match.
    """
    unknown_bytes = secret.encode(SECRET_ENCODING)
    unknown_hash = hash_secret_raw(unknown_bytes, salt, **CRYPTO_PARAMS)

    return unknown_hash == known_hash


def main():
    secret = 'Password'
    secret_hash, secret_salt = hash_secret(secret)
    print(f'len(salt): {len(secret_salt)}, salt: {secret_salt}')
    print(f'len(hash): {len(secret_hash)}, hash: {secret_hash}')


if __name__ == '__main__':
    main()

