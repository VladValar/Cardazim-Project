from __future__ import annotations

import hashlib
from os import PathLike

from Crypto.Cipher import AES
from PIL import Image


class CryptImage:
    def __init__(self, image=None, key_hash=None):
        self.__key_hash = key_hash
        self.__image = image

    @classmethod
    def create_from_path(cls, path: str | PathLike) -> CryptImage:
        """
        Gets a picture and returns a non-encrypted CryptImage
        """
        image = Image.open(path).copy()
        return cls(image)

    def encrypt(self, key: str) -> None:
        """
        Gets a key and encrypts this CryptImage using that key. The hash of the key is sha-256 twice on the key.
        """

        key_bytes = key.encode("utf-8")
        # encrypt twice
        aes_key = hashlib.sha256(key_bytes).digest()
        # Hash used to verify the key
        self.__key_hash = hashlib.sha256(aes_key).digest()
        # Make sure we have RGB
        self.__image = self.__image.convert("RGB")

        width, height = self.__image.size

        plain_image = self.__image.tobytes()

        cipher = AES.new(aes_key, AES.MODE_EAX, nonce=b"arazim")
        encrypted_image = cipher.encrypt(plain_image)
        self.__image = Image.frombytes("RGB", (width, height), encrypted_image)

    def decrypt(self, key: str) -> bool:
        """
        Decrypts the image using the given key. Checks correctness by comparing key to self.__key_hash.
        If the key is incorrect, returns False. If it is true, decrypt the image, update key_hash to be None and return True
        """
        key_bytes = key.encode("utf-8")

        # One hash is the AES-Key
        aes_key = hashlib.sha256(key_bytes).digest()
        key_hash = hashlib.sha256(aes_key).digest()

        if key_hash != self.__key_hash:
            return False

        width, height = self.__image.size
        encrypted_image = self.__image.tobytes()
        # Decrypt
        cipher = AES.new(aes_key, AES.MODE_EAX, nonce=b"arazim")
        plain_image = cipher.decrypt(encrypted_image)

        self.__image = Image.frombytes("RGB", (width, height), plain_image)
        self.__key_hash = None
        return True

    def get_image(self) -> Image.Image:
        return self.__image.copy()

    def get_key_hash(self) -> bytes | None:
        return self.__key_hash

    # def show(self):
    #     self.__image.save("decrypted.png")
