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
import time

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
            if len(decoded_list) >= 50000:
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
            "decoded_file": "decoded_"+file
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
            "IP", "DATETIME", "TIMEZONE", "REQUEST", "URL", "HTTP", "STATUS", "BODY_BYTES_SENT", "REFERER", "USER_AGENT"
        ]
        self.kv_log = []

    def read_log(self, lines):
        for i in lines:
            line_splitited = i.split(" ")
            new_spl = []
            new_spl.append(str(line_splitited[0]))
            new_spl.append(str(line_splitited[3]).replace("[", ""))
            new_spl.append(str(line_splitited[4]).replace("]", ""))
            new_spl.append(str(line_splitited[5]).replace('"', ''))
            new_spl.append(str(line_splitited[6]).replace('"', ''))
            new_spl.append(str(line_splitited[7]).replace('"', ''))
            new_spl.append(str(line_splitited[8]))
            new_spl.append(str(line_splitited[9]))
            new_spl.append(str(line_splitited[10]).replace('"', ''))
            new_spl.append(str(line_splitited[11::]).replace('"', ''))
            single_kv_log = dict(zip(self.to_be_format, new_spl))
            self.kv_log.append(single_kv_log)
        if self.kv_log:
            return self.kv_log
        else:
            return False


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
    parser_convert.set_defaults(parser="convert")

    # Create the Parser for READ the file
    parser_reader = subparsers.add_parser(name="reader")
    # parser_reader.add_argument('--config-format-file', nargs=1, help="Comma seperated file", required=True)
    parser_reader.set_defaults(parser="reader")

    # Arguments
    args = parser.parse_args()
    try:
        file = args.file[0]
        if args.parser == "convert":
            return file_operation(file=file)
        elif args.parser == "reader":
            with open(file, "r") as opened_file:
                # lines = ['157.55.39.53 - - [13/Oct/2019:06:26:06 +0600] "GET /book/88005/the-indian-contract-act--13th-ed- HTTP/1.1" 301 194 "-" "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"']
                lines = opened_file
                print(LOG_Reader().read_log(lines=lines))
            return "Reader..."
    except AttributeError as e:
        parser.print_usage()


if __name__ == "__main__":
    to_execute =  execute()
    if to_execute:
        print(to_execute)
    else:
        to_execute
