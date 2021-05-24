-- Create the table that will be used for the data collection
use redditdata

drop table if exists [raw].topposts_all

CREATE TABLE [raw].topposts_all ( 
    id_art varchar(50), -- id of the post
    subreddit varchar(max), -- subreddit of post
    title varchar(max), -- title of post
    ranking int, -- the rank of the post
    ups int, -- number of up votes(?)
    downs int, -- number of down votes (?)
    over_18 bit, -- flag if the post is over 18 or not
    num_comments int, -- number of comments on post
    score int,    
    created_ts datetime,
    collection_ts datetime,
    constraint pk_postranks primary key (id_art, ranking)
)

SELECT * from [raw].topposts_all