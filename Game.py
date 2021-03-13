import time

app.route('api/conversation',methods = 'POST')
def readconversation(uid: int):
	conn = sqldb.try_open_conn()
    assert conn is not None
    cur = conn.cursor()
    #how to find the uid of the user
    #which pasth should I use
    #

    message = request.values.get('message')
    date = time.strftime("%Y-%m-%d", time.localtime()) 

    with open('','rw') as user_conversation:
    	user_conversation.append((uid,message))

    uid = session.get('uid',)

def append_message(uid, date, message, path):






