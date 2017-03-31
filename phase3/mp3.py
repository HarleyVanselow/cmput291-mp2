from bsddb3 import db
import re
from functools import reduce

string_compare = {
    "text": (lambda text: re.search("text(:)(.+)", text)),
    "date": (lambda text: re.search("date([:|>|<])(.+)", text)),
    "location": (lambda text: re.search("location(:)(.+)", text)),
    "name": (lambda text: re.search("name(:)(.+)", text))
}


def main():
    termdatabase = db.DB()
    termdatabase.open("../phase2/te.idx", None, db.DB_BTREE, db.DB_CREATE, db.DB_DUP)
    datedatabase = db.DB()
    datedatabase.open("../phase2/da.idx")
    tweetdatabase = db.DB()
    tweetdatabase.open("../phase2/tw.idx")

    databases = {"terms": termdatabase, "tweets": tweetdatabase, "dates": datedatabase}
    while 1:
        query = input()
        if query == 'exit':
            break
        run_query(query.lower(), databases)

    for key, value in databases.items(): value.close()


def print_tweet(xml):
    xml = xml.decode("utf-8")
    print("*********************************************")
    print("ID: " + re.search("<id>(.+)</id>", xml).group(1))
    print("Creation date: " + re.search("<created_at>(.+)</created_at>", xml).group(1))
    print("Text: " + re.search("<text>(.+)</text>", xml).group(1))
    print("Name: " + re.search("<name>(.+)</name>", xml).group(1))
    print("Location: " + re.search("<location>(.+)</location>", xml).group(1))
    print("URL: " + re.search("<url>(.+)</url>", xml).group(1))
    print("Retweet count: " + re.search("<retweet_count>(.+)</retweet_count>", xml).group(1))


def print_result_tweets(results, databases):
    for result in results:
        print_tweet(databases["tweets"].get(result))
    print("*********************************************")


def run_query(query, databases):
    matches = []
    for constraint in query.split(' '):
        matches.append(process_query(constraint, databases))
    print_result_tweets(reduce(lambda x, y: set(x) & set(y), matches), databases)


def process_query(query, databases):
    for (info, search) in string_compare.items():
        if search(query) is not None:
            return execute(info, search(query).group(1),search(query).group(2), databases)
    return search_general(query, databases)


def search_date(term, operation, databases):
    print("Searching date...")
    cursor = databases["dates"].cursor()
    key = bytes(term,'utf-8')
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


def search_location(term, databases):
    print("Searching name...")
    cursor = databases["terms"].cursor()
    results = []
    if cursor.set(bytes("l-" + term, 'utf-8')) is None:
        return results
    else:
        results.append(cursor.current()[1])
        while cursor.next_dup() is not None:
            results.append(cursor.current()[1])
    return results


def search_name(term, databases):
    print("Searching name...")
    cursor = databases["terms"].cursor()
    results = []
    if cursor.set(bytes("n-" + term, 'utf-8')) is None:
        return results
    else:
        results.append(cursor.current()[1])
        while cursor.next_dup() is not None:
            results.append(cursor.current()[1])
    return results


def search_text(term, databases):
    print("Searching text...")
    cursor = databases["terms"].cursor()
    results = []
    if cursor.set(bytes("t-" + term, 'utf-8')) is None:
        return results
    else:
        results.append(cursor.current()[1])
        while cursor.next_dup() is not None:
            results.append(cursor.current()[1])
    return results


def search_general(query, databases):
    print("Searching general...")
    results = [search_location(query, databases), search_text(query, databases), search_name(query, databases)]
    return [result for result_set in results for result in result_set]


def execute(info,operation,term, databases):
    if info == "text":
        return search_text(term, databases)
    elif info == "name":
        return search_name(term, databases)
    elif info == "location":
        return search_location(term, databases)
    elif info == "date":
        return search_date(term, operation, databases)

if __name__ == "__main__":
    main()
