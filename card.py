from __future__ import annotations

from os import PathLike
from struct import pack, unpack_from

from PIL import Image

from crypt_image import CryptImage


class Card:
    def __init__(
        self,
        name: str,
        creator: str,
        image: CryptImage,
        riddle: str,
        solution: str | None,
    ):
        self.name = name
        self.creator = creator
        self.__image = image
        self.riddle = riddle
        self.__solution = solution

    def __repr__(self):
        return f"<Card name={self.name}, creator={self.creator}"

    def __str__(self):
        return f"Card {self.name} by {self.creator}\nriddle: {self.riddle}\nsolution: {self.__solution if self.__solution is not None else 'unsolved'}"

    @classmethod
    def create_from_path(
        cls, name: str, creator: str, path: str | PathLike, riddle: str, solution: str
    ) -> Card:
        image = CryptImage.create_from_path(path=path)
        return cls(name, creator, image, riddle, solution)

    def serialize(self) -> bytes:
        """
        Serializes the object by concating the following:
        - Name of the card: uint32 of the length of the name, and then a string of that length.
        - Name of the card creator: uint32 of the length of the name, then a string of that length.
        - Image: Height of the picture (uint32), length of the picture (uint32), The binary data (height x size x 3 for RGB)
        - Hash of the key - the hash in bytes (the length of the hash will be 32 bytes)
        - Riddle - uint32 with the length of the riddle and then a string of that length.
        We use little endian as the format.
        We do NOT concat the solution!
        """
        result = bytearray()
        name_bytes = self.name.encode("utf-8")
        result += pack("<I", len(name_bytes))
        result += name_bytes

        creator_bytes = self.creator.encode("utf-8")
        result += pack("<I", len(creator_bytes))
        result += creator_bytes

        image = self.__image.get_image().convert("RGB")
        width, height = image.size
        image_data = image.tobytes()

        result += pack("<I", width)
        result += pack("<I", height)
        result += pack("<I", len(image_data))
        result += image_data

        key_hash = self.__image.get_key_hash()

        if key_hash is None:
            raise ValueError("Can't serialize an image that is not encrypted!")

        if len(key_hash) != 32:
            raise ValueError("Key hash must be exactly 32 bytes!")

        result += key_hash

        riddle_bytes = self.riddle.encode("utf-8")
        result += pack("<I", len(riddle_bytes))
        result += riddle_bytes

        return bytes(result)

    @classmethod
    def deserialize(cls, data: bytes) -> Card:
        """
        A class method that gets the serialization of the object, and returns the object.
        Serialization will be in the format given in the method serialize.
        As there is no solution, solution will be None.
        """

        # Helpful functions for reading the data. Makes sense to only be in this scope.
        def read_uint32(data: bytes, index: int) -> tuple[int, int]:
            # Because little endian is the serialization format
            if index + 4 > len(data):
                raise ValueError("Unexpected end of data")
            value = unpack_from("<I", data, index)[0]
            return value, index + 4

        def read_bytes(data: bytes, index: int, length: int) -> tuple[bytes, int]:
            if index + length > len(data):
                raise ValueError("Unexpected end of data")
            if length < 0:
                raise ValueError("Length can not be negative!")
            value = data[index : index + length]
            return value, index + length

        def read_string(data: bytes, index: int) -> tuple[str, int]:
            length, index = read_uint32(data, index)
            if length == 0:
                raise ValueError("string can not be empty!")

            try:
                value, index = read_bytes(data, index, length)
            except UnicodeDecodeError:
                raise ValueError("Invalid utf-8 data!")

            return value.decode("utf-8"), index

        index = 0

        name, index = read_string(data, index)

        creator, index = read_string(data, index)

        width, index = read_uint32(data, index)
        height, index = read_uint32(data, index)

        if width <= 0 or height <= 0:
            raise ValueError("Image dimensions must be positive")

        image_length, index = read_uint32(data, index)

        if image_length != 3 * width * height:
            raise ValueError("Must be a valid RGB image!")

        image_data, index = read_bytes(data, index, image_length)
        image = Image.frombytes("RGB", (width, height), image_data)

        # Key hash
        key_hash, index = read_bytes(data, index, 32)

        # Riddle
        riddle, index = read_string(data, index)

        if index != len(data):
            raise ValueError("Invalid data: Trailing bytes!")

        crypt_image = CryptImage(image=image, key_hash=key_hash)

        return cls(
            name=name, creator=creator, image=crypt_image, riddle=riddle, solution=None
        )

    # TESTING FOR THIS! UNCOMMENT TO RUN MAIN.
    # def get_image(self)->CryptImage:
    #     return self.__image

    # def get_solution(self)->str:
    #     return self.__solution


def main():
    # UNCOMMENT THE FUNCTIONS DEFINED TO RUN MAIN. THEY ARE A SECURITY RISK SO MAKE SURE TO COMMENT AGAIN WHEN FINISHED.
    card = Card.create_from_path(
        name="jesus",
        creator="me",
        riddle="What is your favourite color?",
        solution="green",
        path=r"/home/amsha/Cardazim-Project/jesus_dinosaur.png",
    )
    card.get_image().encrypt(card.get_solution())
    data = card.serialize()
    card2 = Card.deserialize(data)
    if card2.get_image().decrypt(card.get_solution()):
        card2.solution = card.get_solution()
    assert repr(card) == repr(card2)
    card2.get_image().get_image().show()


if __name__ == "__main__":
    main()
