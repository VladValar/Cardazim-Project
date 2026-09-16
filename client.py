import argparse
import socket
import sys
from pathlib import Path

from card import Card
from connection import Connection
from crypt_image import CryptImage

###########################################################
####################### YOUR CODE #########################
###########################################################


def send_data(connection: Connection, data: str) -> None:
    connection.send(b"M" + bytes(data, "utf-8"))


def send_card(
    connection: Connection,
    name: str,
    creator: str,
    path: Path,
    riddle: str,
    solution: str,
) -> None:
    print(f"Sending the card {name} by {creator}...")

    crypt_image = CryptImage.create_from_path(path=path)
    crypt_image.encrypt(solution)
    card = Card(
        name=name, creator=creator, image=crypt_image, riddle=riddle, solution=solution
    )
    connection.send(b"C" + card.serialize())


###########################################################
##################### END OF YOUR CODE ####################
###########################################################


def get_args():
    parser = argparse.ArgumentParser(description="Send data to server.")
    parser.add_argument("server_ip", type=str, help="the server's ip")
    parser.add_argument("server_port", type=int, help="the server's port")
    parser.add_argument("name", type=str, help="the name of the card")
    parser.add_argument("creator", type=str, help="the name of the creator of the card")
    parser.add_argument("riddle", type=str, help="the riddle for the card")
    parser.add_argument("solution", type=str, help="the solution of the card")
    parser.add_argument("path", type=Path, help="the path to the image")
    return parser.parse_args()


def main():
    """
    Implementation of CLI and sending data to server.
    """
    args = get_args()
    with Connection(socket.socket(socket.AF_INET, socket.SOCK_STREAM)).connect(
        args.server_ip, args.server_port
    ) as s:
        send_card(
            connection=s,
            name=args.name,
            creator=args.creator,
            riddle=args.riddle,
            solution=args.solution,
            path=args.path,
        )
        print("Done.")


if __name__ == "__main__":
    sys.exit(main())
