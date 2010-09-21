from core.message import Message
from core.message_set import MessageSet
import BeautifulSoup
from datetime import datetime, time, timedelta

def extract_html_data(htmlsms):
    """
    extractsms  --  extract SMS sub_htmls from BeautifulSoup tree of Google Voice SMS HTML.

    Output is a list of dictionaries, one per sub_html.
    """
    msgdict = {}										# accum sub_html items here
    #	Extract all conversations by searching for a DIV with an ID at top level.
    tree = BeautifulSoup.BeautifulSoup(htmlsms)			# parse HTML into tree
    conversations = tree.findAll("div",attrs={"id" : True},recursive=False)
    for conversation in conversations :
        #	For each conversation, extract each row, which is one SMS sub_html.
        rows = conversation.findAll(attrs={"class" : "gc-message-sms-row"})
        for row in rows :								# for all rows
            #	For each row, which is one sub_html, extract all the fields.
            spans = row.findAll("span",attrs={"class" : True}, recursive=False)
            msgitem = {}
            for span in spans :							# for all spans in row
                cl = span["class"].replace('gc-message-sms-', '')
                msgitem[cl] = (" ".join(span.findAll(text=True))).strip()	# put text in dict
            if msgdict.has_key(conversation["id"]):
                msgdict[conversation["id"]].append(msgitem)		# add msg dictionary to list
            else:
                msgdict[conversation["id"]] = [msgitem]
    
    return msgdict

def gv_convos_to_messages(cxn):

    msgs = MessageSet()

    gv_num = cxn.voice.settings['primaryDid']
    convos = cxn.voice.sms().messages
    msgdict = extract_html_data(cxn.voice.sms.html)

    #extract sub-message's html data within each coversation and turn into Message instances
    for convo in convos:
        #get the date of the conversation
        date = convo.displayStartDateTime
        y, mo, d = date.year, date.month, date.day
        for index,sub_html in enumerate(msgdict[convo.id]):
            
            #make sub_html id out of convo id and index of msg within convo
            sub_id = '%s__%s' % (convo.id,index)

            #get time of sub_html
            #this won't understand conversations that wrap around midnight 
            #or noon, unless we use %I instead of %H
            #deal with that later
            try:
                temp_sub_time = datetime.strptime(sub_html['time'],"%I:%M %p")
                h, mi = temp_sub_time.hour, temp_sub_time.minute
                
                sub_time = datetime(y,mo,d,h,mi)
                
                #watch out for midnight rollover!
                if sub_time > (datetime.now()+timedelta(minutes=2)):
                    print "time was %s"
                    sub_time = sub_time - timedelta(days=1)
                
            #if GV appends the date to the html the above errors
            except ValueError:
                sub_time = datetime.strptime(sub_html['time'],"%I:%M %p  (%m/%d/%y)")
            
            if sub_html['from'] == "Me:":
                sub_from = gv_num
                sub_to = convo.phoneNumber
            else:
                sub_from = convo.phoneNumber
                sub_to = gv_num
                
            sub = Message(from_num=sub_from,
                          to_num=sub_to,
                          text=sub_html['text'],
                          id=sub_id,
                          labels=convo.labels,
                          datetime=sub_time,
                          is_read = convo.isRead, #this will make ALL sub-sub_htmls
                                                  #within a conversation unread
                                                  #which is not really ideal
                          connection = cxn)
            msgs.append(sub)

    return msgs
    
    
#for debugging
if __name__ == "__main__":
    msgs = gv_convos_to_messages(conn.voice)
            
