"""
This module allows for reading and writing conversations history files.
"""

__all__ = ['read_messages', 'write_message']

import datetime
import os


def read_messages(fpath: str, from_date: datetime.datetime):
    """
    Reads all history files in the given fpath, returning the messages 
    as a list of (date, uid, msg) tuples.
    """
	contents = []

    start_date = datetime.datetime(from_date.year, from_date.month, from_date.day)
	now = datetime.datetime.now()
    end_date = datetime.datetime(now.year, now.month, now.day)

    while start_date <= end_date:
		formatted_date = from_date.strftime('%d-%m-%Y')
        conversation_file = f'{fpath}/{formatted_date}.conv'

		with open(conversation_file, 'r') as conversation:
			for line in conversation:
				time, uid, message = line.split(';', maxsplit=2)
                contents.append((time, uid, message))

		start_date += datetime.timedelta(days=1)

	return contents


def write_message(fpath: str, date: datetime.datetime, uid: int, message: str):
    """
    Appends the given message to the correct history file in the given 
    fpath in the format: 'date;uid;msg'
    """
    formatted_date = date.strftime('%d-%m-%Y')
    formatted_time = date.strftime('%H-%M-%S')

	if not os.path.isdir(fpath):
		os.mkdir(fpath)

    conversation_file = f'{fpath}/{formatted_date}.conv'
	if not os.path.isfile(conversation_file):
		os.mknod(conversation_file)

	with open(conversation_file, 'a') as conversation:
		conversation.write(f'{formatted_time};{uid};{message}\n')

