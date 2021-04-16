"""
This module allows for reading and writing conversations history files.
"""

__all__ = ['ensure_fpath', 'read_messages', 'write_message']

import datetime
import os


def ensure_fpath(fpath: str):
    """
    Creates the given fpath if it doesnt already exist.
    """
    if not os.path.isdir(fpath):
        print(f'Creating fpath: {fpath}')
        os.mkdir(fpath)


def read_messages(fpath: str, from_date_index: int, from_time_index: int):
    """
    Reads all history files in the given fpath, returning the messages 
    as a list of (date, uid, msg) tuples.
    """
    contents = []

    ensure_fpath(fpath)

    for current, dirs, files in os.walk(fpath):
        for conversation_file in files:
            date_index = int(conversation_file[:-len('.conv')])

            if from_date_index is not None and from_date_index > date_index:
                continue

            print(from_date_index, date_index)

            with open(f'{current}/{conversation_file}', 'r') as conversation:
                for line in conversation:
                    timestamp, datestamp, uid, message = line.split(';', maxsplit=3)
                    time_index = int(f'{timestamp[0:2]}{timestamp[3:]}')

                    if from_time_index is not None and from_time_index >= time_index:
                        continue

                    contents.append((timestamp, datestamp, uid, message))

    return contents


def write_message(fpath: str, date: datetime.datetime, uid: int, message: str):
    """
    Appends the given message to the correct history file in the given 
    fpath in the format: 'time;date;uid;msg'
    """
    date_index = int(f'{date.year}{date.month}{date.day}')

    formatted_date = date.strftime('%d %B %Y')
    formatted_time = date.strftime('%H:%M')

    ensure_fpath(fpath)

    conversation_file = f'{fpath}/{date_index}.conv'
    if not os.path.isfile(conversation_file):
        os.mknod(conversation_file)

    with open(conversation_file, 'a') as conversation:
        conversation.write(f'{formatted_time};{formatted_date};{uid};{message}\n')

