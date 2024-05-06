#!/usr/bin/python3

# imports
import sqlalchemy
import os
import datetime
import zipfile
import io
import json

################################################################################
# helper functions
################################################################################


def remove_nulls(s):
    r'''
    Postgres doesn't support strings with the null character \x00 in them, but twitter does.
    This helper function replaces the null characters with an escaped version so that they can be loaded into postgres.
    Technically, this means the data in postgres won't be an exact match of the data in twitter,
    and there is no way to get the original twitter data back from the data in postgres.

    The null character is extremely rarely used in real world text (approx. 1 in 1 billion tweets),
    and so this isn't too big of a deal.
    A more correct implementation, however, would be to *escape* the null characters rather than remove them.
    This isn't hard to do in python, but it is a bit of a pain to do with the JSON/COPY commands for the denormalized data.
    Since our goal is for the normalized/denormalized versions of the data to match exactly,
    we're not going to escape the strings for the normalized data.

    >>> remove_nulls('\x00')
    ''
    >>> remove_nulls('hello\x00 world')
    'hello world'
    '''
    if s is None:
        return None
    else:
        return s.replace('\x00','')


def get_id_urls(url, connection):
    '''
    Given a url, return the corresponding id in the urls table.
    If no row exists for the url, then one is inserted automatically.

    NOTE:
    This function cannot be tested with standard python testing tools because it interacts with the db.
    '''
    sql = sqlalchemy.sql.text('''
    insert into urls 
        (url)
        values
        (:url)
    on conflict do nothing
    returning id_urls
    ;
    ''')
    res = connection.execute(sql,{'url':url}).first()

    # when no conflict occurs, then the query above inserts a new row in the url table and returns id_urls in res[0];
    # when a conflict occurs, then the query above does not insert or return anything;
    # we need to run a select statement to put the already existing id_urls into res[0]
    if res is None:
        sql = sqlalchemy.sql.text('''
        select id_urls 
        from urls
        where
            url=:url
        ''')
        res = connection.execute(sql,{'url':url}).first()

    id_urls = res[0]
    return id_urls


def insert_tweet(connection,tweet):
    '''
    Insert the tweet into the database.

    Args:
        connection: a sqlalchemy connection to the postgresql db
        tweet: a dictionary representing the json tweet object

    NOTE:
    This function cannot be tested with standard python testing tools because it interacts with the db.
    
    FIXME:
    This function is only partially implemented.
    You'll need to add appropriate SQL insert statements to get it to work.
    '''


    # insert tweet within a transaction;
    # this ensures that a tweet does not get "partially" loaded
    with connection.begin() as trans:
        #THIS BEGINS AND ENDS THE TRANsCATION WITHOUT NEEDED THE ACTUAL CODE

        # skip tweet if it's already inserted
        #MOVED INTOT HERE TO ONLY RUN QUERIES IN THE TRANSACTION
        sql=sqlalchemy.sql.text('''
        SELECT id_tweets 
        FROM tweets
        WHERE id_tweets = :id_tweets
        ''')
        res = connection.execute(sql,{
            'id_tweets':tweet['id'],
            })
        if res.first() is not None:
            return

        ########################################
        # insert into the users table
        ########################################
        
        if tweet['user']['url'] is None:
            user_id_urls = None
        else:
            user_id_urls = get_id_urls(tweet['user']['url'], connection)

        # create/update the user
        
        password = 'test'
        
        sql = sqlalchemy.sql.text('''
            INSERT INTO users
                (id_users, username, password, created_at )
            VALUES
                (:id_users, :username, :password, :created_at)
            ON CONFLICT (id_users) DO NOTHING
            ''')

        #the json we want in the correct format
        par = {
           'id_users':tweet['user']['id'],
            'created_at':tweet.get('created_at', None),
            'updated_at':tweet.get('updated_at', None),
            'id_urls':user_id_urls,
            'password': password,
            'friends_count':tweet.get('friends_count', None),
            'listed_count':tweet.get('listed_count', None),
            'favourites_count':tweet.get('favourites_count', None),
            'statuses_count':tweet.get('statuses_count', None),
            'protected':tweet.get('protected', None),
            'verified':tweet.get('verified', None),
            'username':tweet['user']['screen_name'],
            'name':tweet.get('name', None),
            'location':tweet.get('location', None),
            'description':tweet.get('description', None),
            'withheld_in_countries':tweet.get('withheld_in_countries', None)
            }
        
        print(par['username'])  # Instead of print(screen_name)
        print(par['id_users'])  # Instead of print(id_user)
        print(par['password'])  # Already correct
        
        connection.execute(sql, par)

        ########################################
        # insert into the tweets table
        ########################################

        try:
            text = tweet['extended_tweet']['full_text']
        except:
            text = tweet['text']


        # insert the tweet
        sql=sqlalchemy.sql.text(f'''
            INSERT INTO TWEETS (id_tweets, id_users, created_at, text)
            VALUES (:id_tweets, :id_users, :created_at, :text)
            ON CONFLICT DO NOTHING
            ''')
        
        par = {
            'id_tweets':tweet['id'],
            'id_users':tweet['user']['id'],
            'created_at':tweet.get('created_at',None),
            'text':remove_nulls(text)
            }

        connection.execute(sql, par)

        ########################################
        # insert into the tweet_urls table
        ########################################

        try:
            urls = tweet['extended_tweet']['entities']['urls']
        except KeyError:
            urls = tweet['entities']['urls']

        for url in urls:
            id_urls = get_id_urls(url['expanded_url'], connection)

            sql=sqlalchemy.sql.text('''
                insert into tweet_urls (id_tweets, id_urls)
                values (:id_tweets, :id_urls)
                on conflict do nothing
                ''')
            par = {
                    'id_tweets': tweet['id'],
                    'id_urls': id_urls
                 }
            connection.execute(sql, par)

################################################################################
# main functions
################################################################################

if __name__ == '__main__':
    
    # process command line args
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--db',required=True)
    parser.add_argument('--inputs',nargs='+',required=True)
    parser.add_argument('--print_every',type=int,default=1000)
    args = parser.parse_args()

    # create database connection
    engine = sqlalchemy.create_engine(args.db, connect_args={
        'application_name': 'load_tweets.py',
        })
    connection = engine.connect()

    # loop through the input file
    # NOTE:
    # we reverse sort the filenames because this results in fewer updates to the users table,
    # which prevents excessive dead tuples and autovacuums
    for filename in sorted(args.inputs, reverse=True):
        with zipfile.ZipFile(filename, 'r') as archive: 
            print(datetime.datetime.now(),filename)
            for subfilename in sorted(archive.namelist(), reverse=True):
                with io.TextIOWrapper(archive.open(subfilename)) as f:
                    for i,line in enumerate(f):

                        # load and insert the tweet
                        tweet = json.loads(line)
                        insert_tweet(connection,tweet)

                        # print message
                        if i%args.print_every==0:
                            print(datetime.datetime.now(),filename,subfilename,'i=',i,'id=',tweet['id'])