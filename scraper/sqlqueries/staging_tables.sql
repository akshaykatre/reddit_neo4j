use redditdata

drop table if exists [staging].topposts_all

CREATE TABLE [staging].topposts_all ( 
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
    prev_collectiontime datetime,
    constraint pk_postranks primary key (id_art, ranking)
)

insert into [staging].topposts_all
select tp.*, 
lag(collection_ts, 1) over (partition by id_art order by collection_ts) as prev_collectiontime
from [raw].topposts_all tp 


create table [staging].subreddit (
    subreddit varchar(max),
    ntitles int,
    avgrank numeric, 
    constraint pk_subs primary key (subreddit)
)

insert into [staging].subreddit
select 
tp.subreddit as subreddit,
count(distinct title) as ntitles,
avg(ranking) as avgrankfrom [raw].topposts_all tp
group by subreddit