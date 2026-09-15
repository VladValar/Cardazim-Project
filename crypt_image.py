from Crypto.cipher import AES
import hashlib

class CryptImage:
    def __init__(self, key_hash=None, image=None):
        self.__key_hash=key_hash
        self.__image=image
    def create_from_path(cls, path: Union[str,PathLike]) -> CryptImage:
        '''
        Gets a picture and returns a non-encrypted CryptImage
        '''
        pass

    def encrypt(self,key:str)->None:
        '''
        Gets a key and encrypts this CryptImage using that key. The hash of the key is sha-256 twice on the key.
        '''
        self.__key_hash=key
        for i in range(2):
            self.__key_hash=hashlib.sha256(self.__key_hash).digest()
        key=self.__key_hash=hashlib.sha256(key).digest()
        plain_image=self.__image
        cipher=AES.new(key,AES.MOD_MAX, nonce=b'arazim')
        self.__image=cipher.encrypt(plain_image)