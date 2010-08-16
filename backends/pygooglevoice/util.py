from core import Message, MessageSet
import BeautifulSoup
from datetime import datetime, time

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

def gv_convos_to_messages(voice):

    msgs = MessageSet()

    gv_num = voice.settings['primaryDid']
    convos = voice.sms().messages
    msgdict = extract_html_data(voice.sms.html)

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
            #deal with that later
            temp_sub_time = datetime.strptime(sub_html['time'],"%H:%M %p")
            h, mi = temp_sub_time.hour, temp_sub_time.minute
            sub_time = datetime(y,mo,d,h,mi)
            
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
                          backend = "pygooglevoice")
            msgs.append(sub)

    return msgs
    
    
#for debugging
if __name__ == "__main__":
    msgs = gv_convos_to_messages(conn.voice)
            