import json
from neo4j.v1 import GraphDatabase, basic_auth
import pandas 
import pdb 

def main():
    db_config = json.load(open('db-config.json', 'r'))
    print(db_config['port'])
    driver = GraphDatabase.driver('bolt://{0}:{1}'.format(db_config['host'], db_config['port']), auth=basic_auth(db_config['user'], db_config['pass']))

    session = driver.session()
    print("Gathering data..")
    x = pandas.read_csv("data/reddit_info.csv", delimiter="\t", header=None, names=['rank', 'download_time', 'timestamp', 'subreddit', 'id_art', 'ups', 'downs', 'title', 'num_comments', 'score', 'over_18'],error_bad_lines=False)
    x_df = pandas.DataFrame(x)
    print("Grouping..")
    xj = x.groupby(['subreddit', 'id_art'])

    for xx in xj:
        rank, subreddit, id_art = xx[1]['rank'].values[0], xx[0][0], xx[0][1]
        print(rank, subreddit, id_art)
#        pdb.set_trace()
        query = '''
            MERGE (primary:Rank {name:{Rank}})
            MERGE (secondary:Sub {name:{Subreddit}})
            MERGE (tertiary:ID {name:{ID}})
            MERGE (secondary)-[:HASRANK]->(primary)
            MERGE (tertiary)-[:BELONGSTO]->(secondary)
        '''
        print(query)
        session.run(query, {'Rank': rank, 'Subreddit': subreddit, 'ID':id_art})


    session.close()

if __name__ == '__main__':
    main()
