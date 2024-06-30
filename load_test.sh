#!/bin/sh

files=$(find data/*)
# files="data/geoTwitter21-01-01.zip"

echo '================================================================================'
echo 'load pg_normalized'
echo '================================================================================'
	echo "$files" |  time parallel python3 -u load_tweets.py --db  postgresql://hello_flask:hello_flask@localhost:5432/hello_flask_dev --inputs $file
    #echo "$files" |  python3 -u load_tweets.py --db postgresql://hello_flask:hello_flask@localhost:5432/hello_flask_dev --inputs "$file"
