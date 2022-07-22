#Modified from adamhooper's mbox to overview script
#https://gist.github.com/adamhooper/7250f34aa26246ae18dd805f7ce880a0


import email.message
import mailbox
import sys
import os
import re
from types import NoneType

from numpy import true_divide

script_dir = os.path.dirname(__file__)

### Outputs
csvfilename = 'wordcount.csv'
rel_path = "spams" #directory of individual txt files

abs_file_path = os.path.join(script_dir, rel_path)

# Python's mbox reader finds a way to return Messages that don't
# have these super-important methods. This hack adds them.
setattr(email.message.Message, '_find_body', email.message.MIMEPart._find_body)
setattr(email.message.Message, '_body_types', email.message.MIMEPart._body_types)
setattr(email.message.Message, 'get_body', email.message.MIMEPart.get_body)
setattr(email.message.Message, 'is_attachment', email.message.MIMEPart.is_attachment)
setattr(email.message.Message, 'iter_parts', email.message.MIMEPart.iter_parts)
setattr(email.message.Message, 'iter_attachments', email.message.MIMEPart.iter_attachments)

# Reads an mbox from a file and returns a list of messages.
def read_mbox(filename):
    mbox = mailbox.mbox(filename)
    return mbox.values()

# Returns some text describing a message. Headers at the top, then
# two newlines, then message body as text.
def message_to_text(message):
    metadata = """From: {}
To: {}
Cc: {}
Date: {}
Subject: {}""".format(message['From'], message['To'], message['Cc'], message['Date'], message['Subject'])

    try:
        body_part = message.get_body(('plain',))
        charset =  body_part.get_content_charset() or message.get_content_charset() or 'utf-8'
        body = body_part.get_payload(decode=True).decode(charset)

    except AttributeError as err:
        raise Exception("Unreadable body") 
    
    body = strip_message(body)

    #Pass through word counter
    wordcounter(message['Subject'])
    wordcounter(body)

    return metadata + '\n\n' + body


# Writes a message to a file in the current working directory.

def write_message(message, i):
    try:
        message_to_text(message)
    except:
        return
    newfile = os.path.join(abs_file_path, ('message[%d].txt' % (i)))
    with open(newfile, 'w', encoding="utf-8") as f:
        f.write(message_to_text(message))

from string import digits

# Remove unwanted strings and characters
def strip_message(message):

    str_message = re.sub(r'http\S+', '', message) #remove any
    str_message = str_message.replace("&zwnj;", "")
    str_message = str_message.replace("&nbsp;","")
    str_message = str_message.replace("-","")
    str_message = str_message.replace("—","")
    str_message = str_message.replace("+","")
    return str_message

# Reads the given mbox file and outputs all messages and attachments
# as files in the current working directory.
def main(filename):
    messages = read_mbox(filename)
    for i, message in enumerate(messages):
        write_message(message, i + 1)


stopwordstxt = open("stopwords.txt", "r")
stopwords = stopwordstxt.read().splitlines()
add_stopwords = [u'\u200c',u'\U0001f3b6',u'\U0001f4f7',u'\U0001f3a7',u'\u270d']
stopwords.extend(add_stopwords)

wordcount = {}

def wordcounter(str):
    if(str == None):
        return
    for word in str.lower().split():
        word = word.replace(".","")
        word = word.replace(",","")
        word = word.replace(":","")
        word = word.replace("\"","")
        word = word.replace("!","")
        if word not in stopwords:
            if word not in wordcount:
                wordcount[word] = 1
            else:
                wordcount[word] += 1


#check if string contains number
def containsNumber(str):
    if True in [char.isdigit() for char in str]:
        return True
    else:
        return False

#check if string contains undesirable characters
def containsBadCharacters(str):
    badlist = ['@', '<', '-', '>','(',')','=','*',';','[',']','#','\'','?','div','wrapper','font','img','logo','padding','text','align','border','width', 'mso', 'www','edu','\\','/','&']
    if any(e in str for e in badlist):
        return True
    else:
        return False



### Driver code
filename = sys.argv[1] #first argument is mbox file name
main(filename)


### Word Counter (prints to csv)
import collections
import csv

word_counter = collections.Counter(wordcount)
for word, count in word_counter.most_common(300):
    print(word, ": ", count)

csvfile = open(csvfilename, 'w',newline='')
writer = csv.writer(csvfile)
for word, count in word_counter.most_common():
    if(containsNumber(word) or containsBadCharacters(word)):
        continue
    try:
        row = [word, count]
        writer.writerow(row)
    except:
        continue
    