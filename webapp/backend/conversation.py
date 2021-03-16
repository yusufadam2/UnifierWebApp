import datetime
import os

def read_messages(fpath, from_date):
	contents = []
	end_date = datetime.datetime.now()

	while from_date <= end_date:  
		date_str = from_date.strftime('%d-%m-%Y')  
        
		with open('{}/{}.conv'.format(fpath,date_str),'r') as conversation:
			for line in message:
				contents.append(line.split(';'))

		from_date += datetime.timedelta(days=1)

	return contents


def write_message(fpath, date, uid, message):
	date_file = f'{date}.conv'

	if not os.path.isdir(fpath):
		os.makedirs(fpath)

	date_path = fpath+'/'+date_file

	if os.path.isfile(date_file):
		os.mknod(date_path)

	with open(date_path, 'a') as conversation:
		conversation.write(f'{uid};{message}')
