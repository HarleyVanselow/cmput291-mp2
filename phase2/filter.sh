#!/bin/bash --
sort "../phase1/tweets.txt" | uniq > filteredtweets
sort "../phase1/terms.txt" | uniq > filteredterms
sort "../phase1/dates.txt" | uniq > filtereddates
$perl ./prepare.pl filteredtweets > finaltweets
$perl ./prepare.pl filteredterms > finalterms
$perl ./prepare.pl filtereddates > finaldates
db_load -f finaltweets -T -t hash -c duplicates=1 tw.idx
db_load -f finalterms -T -t btree -c duplicates=1 te.idx
db_load -f finaldates -T -t btree -c duplicates=1 da.idx
