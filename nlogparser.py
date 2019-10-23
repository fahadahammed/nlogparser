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
import datetime
import gzip
import os
import shutil
import time
import urllib.parse
from multiprocessing import Process

_info = {
    "version": 2,
    "changes": [
        "Convert encoded log files to decoded ones. "
        "Extract GZ files and decode. "
    ]
}

# Global variables
dt_now = str(datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
tmp_file_name = "_log_file_" + dt_now + ".log"


def save_decoded_file(list_of_pieces, file):
    copied_list_of_pieces = list_of_pieces.copy()
    decoded_file_name = "decoded_" + file
    with open(decoded_file_name, "a+") as opened_file_to_append:
        for i in copied_list_of_pieces:
            opened_file_to_append.write(i)


def url_decode(file, original_file_name=None):
    with open(file, "r") as opened_file:
        decoded_list = []
        for i in opened_file:
            decoded_piece = urllib.parse.unquote(i)
            if len(decoded_list) == 1000:
                save_decoded_file(list_of_pieces=decoded_list, file=file)
                decoded_list.clear()
                decoded_list.append(decoded_piece)
            else:
                decoded_list.append(decoded_piece)
        if decoded_list:
            save_decoded_file(list_of_pieces=decoded_list, file=file)
    if original_file_name:
        return {
            "file_to_operate": original_file_name,
            "decoded_file": "decoded_" + file
        }
    else:
        return {
            "file_to_operate": file,
            "decoded_file": "decoded_" + file
        }


def file_decompress(file):
    new_f_name = file.replace(".gz", "")
    with gzip.open(file, 'rb') as f_in:
        with open(new_f_name + tmp_file_name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
    file_name = new_f_name + tmp_file_name
    return {
        "original_file": file,
        "new_file_name": file_name
    }


def file_operation(file):
    allowed_file_extensions = {
        "compressed": ['gz'],
        "plain": ['log', 'txt']
    }
    filename_extension = file.lower().split(".")[-1]
    if filename_extension in allowed_file_extensions["compressed"]:
        file_name = file_decompress(file=file)
        original_file_name = file_name["original_file"]
        file_name = file_name["new_file_name"]
    else:
        file_name = file
        original_file_name = None

    # Decode File
    started_at = time.time()

    decoded_file_info = url_decode(file=file_name, original_file_name=original_file_name)
    finished_at = time.time()
    time_took = finished_at - started_at
    decoded_file_info["time_took"] = time_took
    # Remove Junk
    os.remove(file_name)

    return decoded_file_info


class LOG_Reader:
    def __init__(self):
        self.default_format = '$remote_addr - $remote_user [$time_local] ''"$request" $status $body_bytes_sent ''"$http_referer" "$http_user_agent"'
        self.to_be_format = [
            "IP", "DATETIME", "TIMEZONE", "REQUEST", "URL", "HTTP", "STATUS", "REFERRER"
        ]

    def read_log(self, lines, new_format=None):
        kv_log = []
        for i in lines:
            line_splitted = i.split(" ")
            if len(line_splitted) > 1:
                new_spl = []
                try:
                    if not new_format:
                        new_spl.append(str(line_splitted[0]))
                        new_spl.append(str(line_splitted[3]).replace("[", ""))
                        new_spl.append(str(line_splitted[4]).replace("]", ""))
                        new_spl.append(str(line_splitted[5]).replace('"', ''))
                        new_spl.append(str(line_splitted[6]).replace('"', ''))
                        new_spl.append(str(line_splitted[7]).replace('"', ''))
                        new_spl.append(str(line_splitted[8]))
                        new_spl.append(str(line_splitted[10]))
                    else:
                        line_splitted = i.split(" ")[0:13]
                        new_spl.append(str(line_splitted[2]))
                        new_spl.append(str(line_splitted[4]).replace("[", ""))
                        new_spl.append(str(line_splitted[5]).replace("]", ""))
                        new_spl.append(str(line_splitted[7]).replace('"', ''))
                        new_spl.append(str(line_splitted[8]))
                        new_spl.append(str(line_splitted[9]).replace('"', ''))
                        new_spl.append(str(line_splitted[10]))
                        new_spl.append(str(line_splitted[12]).replace('"', ''))
                except IndexError as e:
                    pass
                single_kv_log = dict(zip(self.to_be_format, new_spl))
                kv_log.append(single_kv_log)
        if kv_log:
            return kv_log
        else:
            return False


def execute():
    parser = argparse.ArgumentParser(
        description="nLogParser is a tool which parse your nginx servers logs in a well sorted way.",
        epilog=f"""The version: {_info["version"]} has some specific changes like {_info["changes"]}."""
    )

    # Global
    parser.add_argument('-v', '-V', '--version', action='version',
                        version='%(prog)s {version}'.format(version=_info["version"]))
    parser.add_argument('file', metavar='file', nargs=1, help='file with location')

    # Create Subparser
    subparsers = parser.add_subparsers()

    # Create the Parser for convert the file
    parser_convert = subparsers.add_parser(name="convert")
    parser_convert.set_defaults(parser="convert")

    # Create the Parser for READ the file
    parser_reader = subparsers.add_parser(name="reader")
    parser_reader.add_argument('--site', nargs=1, default=None, help="Is the log in changed format?")
    group_pr = parser_reader.add_mutually_exclusive_group(required=True)
    group_pr.add_argument('--tail', nargs=1, default=5, help="How many lines from the end of the file?")
    group_pr.add_argument('--head', nargs=1, default=5, help="How many lines from the head of the file?")
    parser_reader.set_defaults(parser="reader")

    # Arguments
    args = parser.parse_args()
    try:
        file = args.file[0]
        if args.parser == "convert":
            return file_operation(file=file)
        elif args.parser == "reader":
            with open(file_operation(file=file)["decoded_file"], "r") as opened_file:
                lines = opened_file
                if not args.site:
                    readable_data = LOG_Reader().read_log(lines=lines)
                else:
                    readable_data = LOG_Reader().read_log(lines=lines, new_format=args.site[0])
                if type(args.tail) is list:
                    tail = int(args.tail[0])
                    return readable_data[::-1][0:tail]
                if type(args.head) is list:
                    head = int(args.head[0])
                    return readable_data[0:head]

    except AttributeError as e:
        parser.print_usage()


if __name__ == "__main__":
    to_execute = execute()
    if to_execute:
        print(to_execute)
    else:
        to_execute
