from SgSchool import Crawler
from PostProcess import *
import os
import pandas as pd
from pathlib import Path
from tqdm import tqdm

crawl = False
resume = True
process = True

if crawl:
    crawler = Crawler('')
    schools = pd.read_csv('./school_list.csv')
    if resume:
        downloaded = [os.path.splitext(i.name)[0]
                      for i in list(Path('./table_0').glob("*.csv"))]
        pending_schools = schools.query("name not in @downloaded")
    else:
        pending_schools = schools.copy()

    for school in tqdm(pending_schools.to_dict(orient='records')):
        crawler.crawl_school(school['name'], school['link'])

if process:
    
    tbl0 = process_tbl(tbl_dir='./table_0',
                       clean_fn=clean_table0,
                       outfile='school_info.csv')

    tbl1 = process_tbl(tbl_dir='./table_1',
                       clean_fn=clean_table1,
                       outfile='school_mother_tougue.csv')

    tbl2 = process_tbl(tbl_dir='./table_2',
                       clean_fn=clean_table2,
                       outfile='school_ballot.csv')
