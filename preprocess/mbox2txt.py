#Modified from adamhooper's mbox to overview script
#https://gist.github.com/adamhooper/7250f34aa26246ae18dd805f7ce880a0


import email.message
import mailbox
import sys
import os
import re
from types import NoneType

script_dir = os.path.dirname(__file__)
rel_path = "hams"
abs_file_path = os.path.join(script_dir, rel_path)

# Just ignore these lines.
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
    
    body = remove_bad(body)

    #Pass through word counter
    wordcounter(message['From'])
    wordcounter(message['To'])
    wordcounter(message['Cc'])
    wordcounter(message['Date'])
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

# Remove unwanted strings and characters
def remove_bad(message):
    str1 = re.sub(r'http\S+', '', message)
    str2 = str1.replace("&zwnj;", "")
    str3 = str2.replace("&nbsp;","")
    return str3

# Reads the given mbox file and outputs all messages and attachments
# as files in the current working directory.
def main(filename):
    messages = read_mbox(filename)
    for i, message in enumerate(messages):
        write_message(message, i + 1)


stopwords = ['to','the','you','your','of','and','{','}','\u200c']
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




# Driver code
filename = sys.argv[1]
main(filename)


# Word Counter (prints to console)
import collections

word_counter = collections.Counter(wordcount)
for word, count in word_counter.most_common(10):
    print(word, ": ", count)
