"""
This module provides an abstract interface allowing the creation 
and verification of cryptographically strong hashes.
"""

__all__ = ['CRYPTO_HASH_LEN', 'CRYPTO_SALT_LEN', 'hash_secret', 'verify_secret']

import os

from argon2 import low_level
from argon2.low_level import hash_secret_raw, Type
from typing import Tuple


CRYPTO_HASH_LEN = 512
CRYPTO_SALT_LEN = 512

CRYPTO_PARAMS = {
    'time_cost': 1,
    'memory_cost': 1024 * 512,
    'parallelism': 4,
    'hash_len': CRYPTO_HASH_LEN,
    'type': Type.ID,
}

SECRET_ENCODING = 'utf8'


def hash_secret(secret: str) -> Tuple[bytes, bytes]:
    """
    Hashes the given secret (a utf8 string), returning a tuple of the 
    derived hash and the newly-generated salt used.
    """
    secret_bytes = secret.encode(SECRET_ENCODING)
    secret_salt = os.urandom(CRYPTO_SALT_LEN)
    secret_hash = hash_secret_raw(secret_bytes, secret_salt, **CRYPTO_PARAMS)

    return secret_hash, secret_salt


def verify_secret(secret: str, known_hash: bytes, known_salt: bytes) -> bool:
    """
    Checks whether the given secret (a utf8 string) hashes (using the 
    given salt) to the given known hash. Returns whether the hashes match.
    """
    unknown_bytes = secret.encode(SECRET_ENCODING)
    unknown_hash = hash_secret_raw(unknown_bytes, known_salt, **CRYPTO_PARAMS)

    return unknown_hash == known_hash


def main():
    secret = 'Password'
    secret_hash, secret_salt = hash_secret(secret)
    print(f'len(salt): {len(secret_salt)}, salt: {secret_salt}')
    print(f'len(hash): {len(secret_hash)}, hash: {secret_hash}')

    shouldBeTrue = verify_secret('Password', secret_hash, secret_salt)
    print(f'Same passwords verify? {shouldBeTrue}')

    shouldBeFalse = verify_secret('foobar', secret_hash, secret_salt)
    print(f'Different passwords verify? {shouldBeFalse}')


if __name__ == '__main__':
    main()

