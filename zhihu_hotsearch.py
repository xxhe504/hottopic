#!/usr/bin/env python
# coding: utf-8

# # zhihu_hotsearch
# 知乎大家都在搜    
# 260704: 去掉R2部分代码   

import requests
import traceback
from loguru import logger
import pandas as pd


import pathlib
if '__file__' in locals():
    # .py代码
    ROOTDIR = pathlib.Path(__file__).absolute().parent 
    #logger.remove()
    logger.add(f"{ROOTDIR}/log/zhihu_hotsearch.py.log", rotation="00:00", retention="30 days")  # 一段时间后进行清理 
else:
    # 适合jupyter中
    ROOTDIR = pathlib.Path.cwd() 
import datetime 
今天日期 = (datetime.date.today() + datetime.timedelta()).strftime('%Y%m%d') 


#-----------------------------------------------------------------
def get_topics(debug:bool=False) -> list:
    '''提取大家都在搜话题列表。获取失败返回空列表。
    '''
    topics = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.zhihu.com"
    }
    url = 'https://www.zhihu.com/api/v4/search/hot_search'
    try:
        response = requests.get(url,headers=headers).json()
        在榜日期 = datetime.datetime.now().strftime('%Y%m%d') 
        在榜时间 = datetime.datetime.now().strftime('%Y%m%d_%H:%M:%S') 
        for 元 in response['hot_search_queries']:
            典 = {'话题':元.get('query',''), 
                'label':元.get('label',''),
                '热度':元.get('hot',0),
                'index':元.get('index',''),
                '在榜日期': 在榜日期,
                '在榜时间': 在榜时间 
                }
            topics.append(典)
    except:
        if debug:
            traceback.print_exc()
    return topics 


#-----------------------------------------------------------------
def write_topic_local(save_dir:str, filename_prefix:str='zhihu_hotsearch', debug:bool=False)-> int:
    '''读取一次热搜接口，并写入本地文件。
    '''
    topics = get_topics()
    df = pd.DataFrame(topics)
    logger.info(f'抓取一次热搜榜，得到{len(topics)}个话题 ')
    if debug:
        logger.debug(topics)
    if not topics:
        return 
    save_dir = pathlib.Path(save_dir)
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)
    # 合并csv文件
    今天日期 = (datetime.date.today() + datetime.timedelta()).strftime('%Y%m%d') 
    tsv文件名 = save_dir / f'{filename_prefix}_{今天日期}.tsv'
    if tsv文件名.exists():
        old_df = pd.read_csv(str(tsv文件名), sep='\t', header=0, dtype={'在榜日期':str,}).fillna('')
        logger.info(f'读文件`{tsv文件名}`, 共有{old_df.shape[0]}个话题')
        new_df = pd.concat([old_df, df], ignore_index=True).drop_duplicates(subset=['话题','label']).reset_index(drop=True)
    else:
        new_df = df.copy()
    logger.info(f'写文件`{tsv文件名}`, 共有{new_df.shape[0]}个话题')
    new_df.to_csv(str(tsv文件名), header=True, index=False, sep='\t')
    return 0


if __name__ == '__main__':
    # 本地保存
    save_dir = str(ROOTDIR / 'data' / 'zhihu' )
    errcode = write_topic_local(save_dir)


#!jupyter nbconvert --to python --no-prompt --TemplateExporter.exclude_input_prompt=True --TemplateExporter.exclude_output_prompt=True  zhihu_hotsearch.ipynb




