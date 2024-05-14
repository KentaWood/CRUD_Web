CREATE EXTENSION IF NOT EXISTS postgis;
SET max_parallel_maintenance_workers TO 80;
SET maintenance_work_mem TO '16 GB';
CREATE EXTENSION IF NOT EXISTS RUM;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Setting ON_ERROR_STOP to on ensures that the script will stop executing if an error occurs.
\set ON_ERROR_STOP on

-- Begin a transaction to ensure all changes are made atomically.
BEGIN;

-- The 'urls' table stores unique URLs that are referenced in tweets.
-- 'id_urls' is the primary key that uniquely identifies each URL.
CREATE TABLE urls (
    id_urls BIGSERIAL PRIMARY KEY,
    url TEXT UNIQUE
);

-- The 'users' table stores information about each user, including their credentials.
-- 'id_users' is the primary key that uniquely identifies each user.
-- 'username_users' stores the username of the user.
-- 'pwd_users' stores the password for the user, typically expected to be stored in a hashed format for security.
-- 'created_at' records the datetime when the user's account was created.
-- 'updated_at' records the datetime when the user's information was last updated.
CREATE TABLE users (
    id_users BIGINT PRIMARY KEY,
    -- username_users TEXT,
    -- pwd_users TEXT,
    username TEXT,
    password TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- The 'tweets' table stores information about each tweet.
-- 'id_tweets' is the primary key that uniquely identifies each tweet.
-- 'id_users' links each tweet to a user and is a foreign key that references the 'users' table.
-- 'created_at' records the datetime when the tweet was created.
-- 'text' contains the content of the tweet.
CREATE TABLE tweets (
    id_tweets SERIAL BIGINT PRIMARY KEY,
    id_users BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    text TEXT,
    FOREIGN KEY (id_users) REFERENCES users(id_users)
);

-- The 'tweet_urls' table associates tweets with URLs.
-- This table uses a composite primary key consisting of 'id_tweets' and 'id_urls', meaning a tweet can link to multiple URLs and a URL can be linked from multiple tweets.
-- Foreign keys reference the 'tweets' and 'urls' tables, establishing the relationship between tweets, URLs, and this association table.
CREATE TABLE tweet_urls (
    id_tweets BIGINT,
    id_urls BIGINT,
    PRIMARY KEY (id_tweets, id_urls),
    FOREIGN KEY (id_tweets) REFERENCES tweets(id_tweets),
    FOREIGN KEY (id_urls) REFERENCES urls(id_urls)
);


-- Index to enhance the speed of full-text search on the 'text' column using PostgreSQL's full-text search capabilities
-- This index is beneficial for more complex text searches that go beyond simple LIKE queries
CREATE INDEX idx_fts_tweets_text ON tweets USING RUM (to_tsvector('english', text));

-- Index on the foreign key in the 'tweets' table to speed up joins with the 'users' table
CREATE INDEX idx_tweets_users ON tweets (id_users);

-- Index for improving the efficiency of ordering tweets by their creation date
-- Especially useful for queries that sort results to show the most recent tweets first
CREATE INDEX idx_tweets_created_at ON tweets (created_at DESC);

CREATE SEQUENCE tweets_id_tweets_seq;





-- Commit the transaction to finalize all changes made during this transaction block.
COMMIT;


