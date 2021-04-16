"""
This module allows for reading and writing conversations history files.
"""

__all__ = ['read_messages', 'write_message']

import datetime
import os


def read_messages(fpath: str, from_date: datetime.date):
    """
    Reads all history files in the given fpath, returning the messages 
    as a list of (date, uid, msg) tuples.
    """
	contents = []

    start_date = from_date
    end_date = datetime.date.today()

    while start_date <= end_date:
		formatted_date = from_date.strftime('%d %B %Y')
        conversation_file = f'{fpath}/{formatted_date}.conv'

		with open(conversation_file, 'r') as conversation:
			for line in conversation:
				time, date, uid, message = line.split(';', maxsplit=3)
                contents.append((timestamp, datestamp, uid, message))

		start_date += datetime.timedelta(days=1)

	return contents


def write_message(fpath: str, date: datetime.datetime, uid: int, message: str):
    """
    Appends the given message to the correct history file in the given 
    fpath in the format: 'time;date;uid;msg'
    """
    formatted_date = date.strftime('%d %B %Y')
    formatted_time = date.strftime('%H:%M')

	if not os.path.isdir(fpath):
		os.mkdir(fpath)

    conversation_file = f'{fpath}/{formatted_date}.conv'
	if not os.path.isfile(conversation_file):
		os.mknod(conversation_file)

	with open(conversation_file, 'a') as conversation:
		conversation.write(f'{formatted_time};{formatted_date};{uid};{message}\n')

