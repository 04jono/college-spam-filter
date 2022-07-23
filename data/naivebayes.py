# Multinomial Naive Bayes Classifier without ML libraries, based on the bag of words model

import csv
import re

# Copied from datareader
def containsNumber(str):
    if True in [char.isdigit() for char in str]:
        return True
    else:
        return False

#check if string contains undesirable characters
def containsBadCharacters(str):
    badlist = ['@', '<', '-', '>','(',')','=','*',';','[',']','#','\'','?','div','wrapper','font','img','logo','padding','text','align','border','width', 'mso', 'www','\\','/','&']
    if any(e in str for e in badlist):
        return True
    else:
        return False

# Remove unwanted strings and characters
def strip_message(message):

    str_message = re.sub(r'http\S+', '', message) #remove any
    str_message = str_message.replace("&zwnj;", "")
    str_message = str_message.replace("&nbsp;","")
    str_message = str_message.replace("-","")
    str_message = str_message.replace("—","")
    str_message = str_message.replace("+","")
    return str_message



### Inputs
hamcsv = 'hamwordcount.csv'
spamcsv = 'spamwordcount.csv'

# ML parameters
alpha = 1

# Build probabilities
ham_hist = {}

with open(hamcsv, 'r') as f:
    reader = csv.reader(f)
    ham_hist = {rows[0]:rows[1] for rows in reader}

ham_total = int(ham_hist.get('$TOTAL'))
ham_probs = {}
ham_probs = {key:(int(value)+alpha)/ham_total for key, value in ham_hist.items()}

spam_hist = {}

with open(spamcsv, 'r') as f:
    reader = csv.reader(f)
    spam_hist = {rows[0]:rows[1] for rows in reader}

spam_total = int(spam_hist.get('$TOTAL'))
spam_probs = {}
spam_probs = {key:(int(value)+alpha)/spam_total for key, value in spam_hist.items()}

prior_ham = int(ham_hist.get('$NUMMESSAGES')) / (int(ham_hist.get('$NUMMESSAGES')) + int(spam_hist.get('$NUMMESSAGES')))
prior_spam = int(spam_hist.get('$NUMMESSAGES')) / (int(ham_hist.get('$NUMMESSAGES')) + int(spam_hist.get('$NUMMESSAGES')))

def containsNumber(str):
    if True in [char.isdigit() for char in str]:
        return True
    else:
        return False


def evaluate(message):

    #Print to console message (debug)
    print("Message: ", message)

    #Clean up message
    message = strip_message(message)

    for word in message.lower().split():
        # Clean up message

        if(containsNumber(word) or containsBadCharacters(word)):
            continue
        word = word.replace(".","")
        word = word.replace(",","")
        word = word.replace(":","")
        word = word.replace("\"","")
        word = word.replace("!","")

        ham_likelihood = prior_ham
        # Evaluate against hams
        if word in ham_probs.keys():
            ham_likelihood *= ham_probs.get(word)
        else:
            ham_likelihood *= alpha/ham_total

        spam_likelihood = prior_spam
        # Evaluate against spams
        if word in spam_probs.keys():
            spam_likelihood *= spam_probs.get(word)
        else:
            spam_likelihood *= alpha/spam_total
    
    # Print to console classification (debug)
    print("ham score: ", ham_likelihood)
    print("spam score: ", spam_likelihood)
    print("final eval: ", "spam" if spam_likelihood > ham_likelihood else "ham")


## Script to execute
evaluate("How can one summer change your life? This summer alone, Westminster students are working for more than 60 different businesses and organizations, ranging from theme parks to international accounting firms. And, if research is your thing, you can also apply to our Summer Research Fellows program and spend the summer conducting in-depth research with a Westminster faculty mentor. The Summer 2022 student-faculty pairs are working on research projects in biology, chemistry, biochemistry, neuroscience and English.")

print("\n")

evaluate("Jonathan, Don’t sweat it, donate it! Hello Jonathan, Do you have a long to-do list this summer? Does it include figuring out what to do with that car that’s been sitting in your driveway for months? Don’t sweat it, donate it! Music for All can use the proceeds to help continue to create, provide, and expand positively life-changing experiences through music for all. Vehicle donations are tax-deductible, and we work to get the highest return per vehicle for us and for your tax benefit. In most cases, when the driver arrives for your tax-deductible gift, you’ll be provided with the donation receipt. You will be mailed a thank-you letter within 30 days of the sale of the vehicle, which also serves as a donation tax receipt. ")

        

            







