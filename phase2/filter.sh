#!/bin/bash
for unfiltered in "~/Programming/cmput291-mp2/phase1/tweets.txt" "~/Programming/cmput291-mp2/phase1/terms.txt"
do
	echo "Filtering $unfiltered"
	cat $unfiltered
done
