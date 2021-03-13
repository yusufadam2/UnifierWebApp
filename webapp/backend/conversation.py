import datetime
import re

def read_message(fpath,fromDate):
	contents = []
    begin_date = datetime.datetime.strptime(fromDate, '%d-%m-%Y')  
    end_date = datetime.datetime.now()

    while begin_date <= end_date:  
        date_str = begin_date.strftime('%d-%m-%Y')  
        
		with open('{}/{}.conv'.format(fpath,date_str),'r') as message:
			for line in message.readlines():
				contents.append(re.findall(r'(.+?);(.+?)'),line)

		begin_date += datetime.timedelta(days=1)

	return contents


def write_message(uid,fpath,message,date):
	date_file = f'{date}.conv'

	if not (os.path.isdir(fpath)):
		os.makedirs(fpath)

	date_path = fpath+date_file
	os.mknod(date_path)

	with open(date_file, 'a') as conversation:
		conversation.write(f'{uid};{message}')
