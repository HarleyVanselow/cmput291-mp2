#!/bin/bash
sort "../phase1/tweets.txt" | uniq > filteredtweets
sort "../phase1/terms.txt" | uniq > filteredterms
sort "../phase1/dates.txt" | uniq > filtereddates

