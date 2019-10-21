#  Project nlogparser is developed by Fahad Ahammed on 10/20/19, 7:12 PM.
#
#  Last modified at 10/20/19, 7:11 PM.
#
#  Github: fahadahammed
#  Email: obak.krondon@gmail.com
#  Location: Dhaka, Bangladesh
#
#  Copyright (c) 2019. All rights reserved.
import argparse
import urllib.parse
import os
import sys
import datetime
import gzip
import shutil

_info = {
    "version": 1,
    "changes": [
        "Convert encoded log files to decoded ones. "
        "Extract GZ files and decode. "
    ]
}

# Global variables
dt_now = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
tmp_file_name = "_log_file_" + dt_now + ".log"


def save_decoded_file(list_of_pieces, file):
    decoded_file_name = "decoded_" + file
    with open(decoded_file_name, "a+") as opened_file_to_append:
        if opened_file_to_append.write(list_of_pieces):
            return True
        else:
            return False

def url_decode(file):
    decoded_list = []
    with open(file, "r") as opened_file:
        for i in opened_file:
            decoded_list.append(i)
            decoded_piece = urllib.parse.unquote(i)
            if len(decoded_list) >= 5:
                save_decoded_file(list_of_pieces=decoded_piece, file=file)
                decoded_list.clear()
                decoded_list.append(decoded_piece)
            else:
                decoded_list.append(decoded_piece)
    save_decoded_file(list_of_pieces=decoded_piece, file=file)
    print(len(decoded_list))
    return True


def file_decompress(file):
    new_f_name = file.replace(".gz", "")
    with gzip.open(file, 'rb') as f_in:
        with open(new_f_name + tmp_file_name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    file_name = new_f_name + tmp_file_name
    return file_name


def file_operation(file):
    allowed_file_extensions = {
        "compressed": ['gz'],
        "plain": ['log', 'txt']
    }
    filename_extension = file.lower().split(".")[-1]
    if filename_extension in allowed_file_extensions["compressed"]:
        file_name = file_decompress(file=file)
    else:
        file_name = file

    # Decode File
    print(url_decode(file=file_name))
    # os.remove(file_name)

    return file_name


def execute():
    parser = argparse.ArgumentParser(
        description="nLogParser is a tool which parse your nginx servers logs in a well sorted way.",
        epilog=f"""The version: {_info["version"]} has some specific changes like {_info["changes"]}."""
    )

    # Global
    parser.add_argument('-v', '-V', '--version', action='version', version='%(prog)s {version}'.format(version=_info["version"]))
    parser.add_argument('file', metavar='file', nargs=1, help='file with location')

    # Create Subparser
    subparsers = parser.add_subparsers()

    # Create the Parser for convert the file
    parser_convert = subparsers.add_parser(name="convert")

    # Create the Parser for READ the file
    parser_reader = subparsers.add_parser(name="read")

    # Arguments
    args = parser.parse_args()
    try:
        file = args.file[0]
        file_operation(file=file)

        return args
    except AttributeError as e:
        parser.print_usage()


if __name__ == "__main__":
    execute()
