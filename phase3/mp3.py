import html
from bsddb3 import db
import re
from functools import reduce

string_compare = {
    "text": (lambda text: re.search("text(:)(.+)", text)),
    "date": (lambda text: re.search("date([:|>|<])(.+)", text)),
    "location": (lambda text: re.search("location(:)(.+)", text)),
    "name": (lambda text: re.search("name(:)(.+)", text))
}
term_types = ["text", "location", "name"]


def print_help():
    print("""Commands:
alphanumeric    ::= [0-9a-zA-Z_]
date            ::= year '/' month '/' day
datePrefix      ::= 'date' (':' | '>' | '<')
dateQuery       ::= dataPrefix date
termPrefix      ::= ('text' | 'name' | 'location') ':'
term            ::= alphanumeric
termPattern     ::= alphanumeric '%'
termQuery       ::= termPrefix? (term | termPattern)
expression      ::= termQuery | dateQuery
query           ::= expression | (expression whitespace)+""")


def main():
    termdatabase = db.DB()
    termdatabase.open("../phase2/te.idx", None, db.DB_BTREE, db.DB_CREATE, db.DB_DUP)
    datedatabase = db.DB()
    datedatabase.open("../phase2/da.idx")
    tweetdatabase = db.DB()
    tweetdatabase.open("../phase2/tw.idx")

    databases = {"terms": termdatabase, "tweets": tweetdatabase, "dates": datedatabase}
    while 1:
        query = input("Enter your query #>")
        if query == 'exit':
            break
        if query == 'help':
            print_help()
        if query == "":
            pass
        else:
            run_query(query.lower(), databases)
    for key, value in databases.items(): value.close()


def print_tweet(xml):
    xml = html.unescape(xml.decode("utf-8"))
    print("*********************************************")
    print("ID: " + re.search("<id>(.+)</id>", xml).group(1))
    field = re.search("<created_at>(.+)</created_at>", xml)
    if field is not None:
        print("Creation date: " + field.group(1))

    field = re.search("<text>(.+)</text>", xml)
    if field is not None:
        print("Text: " + field.group(1))

    field = re.search("<name>(.+)</name>", xml)
    if field is not None:
        print("Name: " + field.group(1))

    field = re.search("<location>(.+)</location>", xml)
    if field is not None:
        print("Location: " + field.group(1))

    field = re.search("<url>(.+)</url>", xml)
    if field is not None:
        print("URL: " + field.group(1))

    field = re.search("<retweet_count>(.+)</retweet_count>", xml)
    if field is not None:
        print("Retweet count: " + field.group(1))


def print_result_tweets(results, databases):
    for result in results:
        print_tweet(databases["tweets"].get(result))
    print("*********************************************")


def run_query(query, databases):
    matches = []
    for constraint in query.split(' '):
        if constraint == "":
            continue
        matches.append(process_query(constraint, databases))
    
    print_result_tweets(set(reduce(lambda x, y: set(x) & set(y), matches)), databases)


def process_query(query, databases):
    for (info, search) in string_compare.items():
        if search(query) is not None:
            return execute(info, search(query).group(1), search(query).group(2), databases)
    return search_general(query, databases)


def search_date(term, operation, databases):
    print("Searching date...")
    cursor = databases["dates"].cursor()
    key = bytes(term, 'utf-8')
    results = []
    if operation == ":":
        if cursor.set(key) is None:
            return results
        else:
            results.append(cursor.current()[1])
            while cursor.next_dup() is not None:
                results.append(cursor.current()[1])
    elif operation == ">":
        if cursor.set_range(key) is None:
            return results
        else:
            if cursor.current()[0] == key:
                results.append(cursor.next_nodup()[1])
            else:
                results.append(cursor.current()[1])
            while cursor.next() is not None:
                results.append(cursor.current()[1])
    elif operation == "<":
        cursor.set_range(key)
        if cursor.prev() is None:
            return results
        else:
            results.append(cursor.current()[1])
            while cursor.prev() is not None:
                results.append(cursor.current()[1])
    return results


def matches_wildcard(key, wildkey):
    term = key.decode("utf-8")[2:]
    pattern = wildkey.replace("%", ".+")
    print("Term: " + term + ", pattern: " + pattern)
    return re.search(pattern, term) is not None


def search_term(term_type, term, databases):
    cursor = databases["terms"].cursor()
    results = []
    # Wildcard search
    if term[-1] == "%":
        print("Searching term with wildcard...")
        key = bytes(term_type[0] + "-" + term[0:-1], 'utf-8')
        print(key)
        if cursor.set_range(key) is None:
            print("No results")
            return results
        else:
            while cursor.current() is not None and matches_wildcard(cursor.current()[0], term):
                if cursor.current()[1] not in results: results.append(cursor.current()[1])
                cursor.next()
    # Regular search
    else:
        print("Searching term...")
        key = bytes(term_type[0] + "-" + term, 'utf-8')
        print(key)
        if cursor.set(key) is None:
            print("No results")
            return results
        else:
            results.append(cursor.current()[1])
            while cursor.next_dup() is not None:
                results.append(cursor.current()[1])

    return results


def search_general(query, databases):
    print("Searching general...")
    results = [search_term(term_type, query, databases) for term_type in term_types]
    return [result for result_set in results for result in result_set]


def execute(info, operation, term, databases):
    if info in term_types:
        return search_term(info, term, databases)
    elif info == "date":
        return search_date(term, operation, databases)


if __name__ == "__main__":
    main()
