import re
from shutil import rmtree
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tqdm import tqdm
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import re
import os
pd.options.mode.chained_assignment = None

import re


def clean_table0(filename):
    name = os.path.splitext(filename)[0]
    tbl0 = pd.read_csv(f'./table_0/{filename}')
    res = tbl0.set_index('School Info').T
    res['SchoolName'] = name
    cols = res.columns.tolist()
    cols.pop(cols.index('SchoolName'))
    cols = ['SchoolName'] + cols
    return res[cols]


def clean_table1(filename):
    name = os.path.splitext(filename)[0]
    tbl = pd.read_csv(f'./table_1/{filename}')
    tbl = tbl.rename(columns = {'Mother Tongue': 'Type'})
    tbl = tbl.melt('Type', var_name = 'MotherTongue')
    tbl = tbl.loc[tbl['value'] == '✅',:].drop(columns = 'value')
    tbl['SchoolName'] = name
    return tbl[['SchoolName','Type','MotherTongue']]


def clean_table2(filename, long_form=True):
    name = os.path.splitext(filename)[0]
    tbl = pd.read_csv(f'./table_2/{filename}')
    tbl['SchoolName'] = name

    def parse_yr_tbl(tbl_yr):
        yr = tbl_yr.iloc[0, 0]
        tbl_yr = tbl_yr.iloc[1:, :]
        tbl_yr['Category'] = tbl_yr['Year'].map(
            lambda x: re.sub('\\W+', '', x)).values
        tbl_yr['Year'] = yr
        return tbl_yr

    res = []
    for i in range(tbl.shape[0] // 4):
        tbl_yr = tbl.iloc[(i * 4): (i+1)*4, :]
        res += [parse_yr_tbl(tbl_yr)]
    res = pd.concat(res)
    if long_form:
        res = res.drop(columns='Total').melt(
            ['Year', 'SchoolName', 'Category'],
            value_name='Count', var_name='Phase')
        res["Count"] = res["Count"].map(lambda x: str(x).split('\n')[0].strip())
        na_values = ["-","0","0.0"]
        res = res.query("Count not in @na_values")
        
    cols = res.columns.tolist()
    cols.pop(cols.index('SchoolName'))
    cols = ['SchoolName'] + cols
    
    return res[cols]

def process_tbl(tbl_dir='./table_0', clean_fn=clean_table0, outfile='school_info.csv'):
    df_tbl0 = []
    for f in tqdm(list(Path(tbl_dir).glob("*.csv")), desc=f"preparing {outfile}"):
        try:
            df_tbl0 += [clean_fn(f.name)]
        except:
            print(f.name)
    df_tbl0 = pd.concat(df_tbl0)
    df_tbl0.to_csv(outfile, index=False)
    return df_tbl0