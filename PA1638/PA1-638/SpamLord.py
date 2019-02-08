import sys
import os
import re
import pprint

email_regex_normal = '(\w[-\w-]+\s?)(?:@|&#x40;|&#64;|WHERE|\s+at|AT\s+|\(at|AT\))(\s?[-\w-]+\s?)(?:\s+dot|DOT\s+|\.|;)?(\s?[-\w-]+\s?)?(?:\s+dot|DOT\s+|\.|;|DOM)(\s?[\-a-zA-Z\-]+)'
#(\w[-\w-]+\s?)(?:@|[&#x40;]|\s+at|AT\s+|\(at|AT\))(\s?[-\w-]+\s?)(?:\s+dot|DOT\s+|\.)?(\s?[-\w-]+\s?)?(?:\s+dot|DOT\s+|\.)(\s?[\-a-zA-Z\-]+)'
#(\w+\s?)@(\s?\w+\s?)(\.\s?\w+\s?)?(\.\s?[a-zA-Z]+)'
#(\w+)(\s?)@(\s?)(\w+)\.?(\w+)?.([a-zA-Z]+)'
email_regex_script = 'obfuscate\(\'(\w+)(?:\s*\;|DOT|dot|\.\s*)(\w+)\'\,\'(\w+)\'\)'
phone_regex_normal = '(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})'
#\(?([0-9]{3})\)?([ .-]?)([0-9]{3})\2([0-9]{4})'
#(\+*\d{1,})*[ |\(]*(\d{3})[^\d\w]*(\d{3})[^\d\w]*(\d{4})'
#(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'


""" 
TODO
This function takes in a filename along with the file object (actually
a StringIO object) and
scans its contents against regex patterns. It returns a list of
(filename, type, value) tuples where type is either an 'e' or a 'p'
for e-mail or phone, and value is the formatted phone number or e-mail.
The canonical formats are:
     (name, 'p', '###-###-#####')
     (name, 'e', 'someone@something')
If the numbers you submit are formatted differently they will not
match the gold answers

NOTE: ***don't change this interface***

NOTE: You shouldn't need to worry about this, but just so you know, the
'f' parameter below will be of type StringIO. So, make
sure you check the StringIO interface if you do anything really tricky,
though StringIO should support most everything.
"""
def process_file(name, f):
    # note that debug info should be printed to stderr
    # sys.stderr.write('[process_file]\tprocessing file: %s\n' % (path))
    res = []
    for line in f:
        matches1 = re.findall(email_regex_normal,line)
        matches3 = re.findall(phone_regex_normal,line)
        matches2 = re.findall(email_regex_script,line)
        #print ("matches:{}".format(matches))
        for m in matches1:
            m = ' '.join(m).split()
            if m[0].lower() == "server" :
                continue
                
            if len(m) == 3:
                email = "{}@{}.{}".format(m[0].strip(),m[1].strip(),m[2].strip())
                if "-" in email:
                    x = email.count("-")
                    if x >= 4:
                        email = email.replace("-","")
                    
                res.append((name,'e',email))
            if len(m) == 4:
                email = "{}@{}.{}.{}".format(m[0].strip(),m[1].strip(),m[2].strip(),m[3].strip())
                if "-" in email:
                    x = email.count("-")
                    if x >= 4:
                        email = email.replace("-","")
                res.append((name,'e',email))
        for m in matches2:
            m = ' '.join(m).split()
            if len(m) == 3:
                email = "{}@{}.{}".format(m[2],m[0],m[1])
                res.append((name,'e',email))
                
        for m in matches3:
            m = ' '.join(m).split()
#            if m[0] == '':
#                phone = "{}-{}-{}".format(m[1],m[2],m[3])
            if len(m) == 3:
                phone = "{}-{}-{}".format(m[0],m[1],m[2])
                res.append((name,'p',phone))
    return res
      
"""
You should not need to edit this function, nor should you alter
its interface
"""
def process_dir(data_path):
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
            continue
        path = os.path.join(data_path,fname)
        f = open(path,'r')
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list

"""
You should not need to edit this function.
Given a path to a tsv file of gold e-mails and phone numbers
this function returns a list of tuples of the canonical form:
(filename, type, value)
"""
def get_gold(gold_path):
    # get gold answers
    gold_list = []
    f_gold = open(gold_path,'r')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list

"""
You should not need to edit this function.
Given a list of guessed contacts and gold contacts, this function
computes the intersection and set differences, to compute the true
positives, false positives and false negatives.  Importantly, it
converts all of the values to lower case before comparing
"""
def score(guess_list, gold_list):
    guess_list = [(fname, _type, value.lower()) for (fname, _type, value) in guess_list]
    gold_list = [(fname, _type, value.lower()) for (fname, _type, value) in gold_list]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    #print 'Guesses (%d): ' % len(guess_set)
    #pp.pprint(guess_set)
    #print 'Gold (%d): ' % len(gold_set)
    #pp.pprint(gold_set)
    print ('True Positives (%d): ' % len(tp))
    pp.pprint(tp)
    print ('False Positives (%d): ' % len(fp))
    pp.pprint(fp)
    print ('False Negatives (%d): ' % len(fn))
    pp.pprint(fn)
    print ('Summary: tp=%d, fp=%d, fn=%d' % (len(tp),len(fp),len(fn)))

"""
You should not need to edit this function.
It takes in the string path to the data directory and the
gold file
"""
def main(data_path, gold_path):
    guess_list = process_dir(data_path)
    gold_list =  get_gold(gold_path)
    score(guess_list, gold_list)

"""
commandline interface takes a directory name and gold file.
It then processes each file within that directory and extracts any
matching e-mails or phone numbers and compares them to the gold file
"""
if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print ('usage:\tSpamLord.py <data_dir> <gold_file>')
        #sys.exit(0)
        exit
    main(sys.argv[1],sys.argv[2])
