import sys
import re


def genXMLRegEx(name):
    return '(%s(.*)%s)' % ('<'+name+'>', '</'+name+'>')


def write_tweets(line,file):
    find_id = re.search(genXMLRegEx('id'), line)
    if find_id is not None:
        file.write(find_id.group(2)+":"+line)


def write_dates(line,file):
    find_date = re.search(genXMLRegEx('created_at'), line)
    find_id = re.search(genXMLRegEx('id'), line)
    if find_id is not None and find_date is not None:
        file.write(find_date.group(2)+':'+find_id.group(2)+"\n")


def filter_special(term):
    regex2 = re.compile('\&\#.[0-9]+\;')
    term = regex2.sub("",term)
    regex1 = re.compile('[^a-zA-Z0-9_]')
    return regex1.sub(' ', term)


def find_terms_in(field,line,file):
    find_id = re.search(genXMLRegEx('id'),line)
    find_field_text = re.search(genXMLRegEx(field),line)
    if find_id is not None and find_field_text is not None:
        raw_terms = find_field_text.group(2).split(' ')
        bad_chars_are_spaces = list(map(lambda x: filter_special(x), raw_terms))
        all_terms = []
        for term in bad_chars_are_spaces:
            all_terms += term.split(' ')
        filtered = list(filter(lambda x: len(x) > 2, all_terms))
        for term in filtered:
            file.write(field[0]+"-"+term.lower()+":"+find_id.group(2)+"\n")


def write_terms(line,file):
    find_terms_in('text',line,file)
    find_terms_in('name',line,file)
    find_terms_in('location',line,file)


def process(line,write_to):
    write_tweets(line,write_to['tweets'])
    write_dates(line,write_to['dates'])
    write_terms(line,write_to['terms'])


def main(file):
    tweets = open('tweets.txt', 'w')
    terms = open('terms.txt', 'w')
    dates = open('dates.txt', 'w')
    write_to = {'tweets':tweets,'terms':terms,'dates':dates}
    with open(file) as f:
        for line in f.readlines():
            process(line,write_to)
    tweets.close()
    terms.close()
    dates.close()

if __name__ == '__main__':
    main(sys.argv[0])