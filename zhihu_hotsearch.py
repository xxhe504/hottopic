#!/usr/bin/env python
# coding: utf-8

# # zhihu_hotsearch
# 知乎大家都在搜    
# 261007：一律写入r2  

import requests
import traceback
from loguru import logger
import pandas as pd
from io import StringIO
import r2_util as r2


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
        new_df = pd.concat([old_df, df], ignore_index=True).drop_duplicates(subset=['话题']).reset_index(drop=True)
    else:
        new_df = df.copy()
    logger.info(f'写文件`{tsv文件名}`, 共有{new_df.shape[0]}个话题')
    new_df.to_csv(str(tsv文件名), header=True, index=False, sep='\t')
    return 0


#-----------------------------------------------------------------
def write_topic_r2(filename_prefix:str='zhihu_hotsearch', debug:bool=False)-> str:
    '''读取一次热搜接口，并写入R2。
    '''
    topics = get_topics()
    df = pd.DataFrame(topics)
    logger.info(f'抓取一次热搜榜，得到{len(topics)}个话题 ')
    if debug:
        logger.debug(topics)
    if not topics:
        return ''
    # 合并csv文件
    今天日期 = (datetime.date.today() + datetime.timedelta()).strftime('%Y%m%d') 
    tsv文件名 = f'{filename_prefix}_{今天日期}.tsv'
    if r2.file_exists_in_r2_zhihu(tsv文件名):
        tsv_text = r2.read_r2_tsv(tsv文件名)
        # 转 pandas DataFrame 查看
        old_df = pd.read_csv(StringIO(tsv_text), sep="\t", header=0, dtype={'在榜日期':str,}).fillna('')
        logger.info(f'下载文件`{tsv文件名}`, 共有{old_df.shape[0]}个话题')
        new_df = pd.concat([old_df, df], ignore_index=True).drop_duplicates(subset=['话题']).reset_index(drop=True)
    else:
        new_df = df.copy()

    # df转TSV字符串
    buf = StringIO()
    # sep制表符、不输出索引、utf8编码
    new_df.to_csv(buf, sep="\t", index=False, header=True, encoding="utf-8")
    tsv_text = buf.getvalue()
    logger.info(f'上传文件`{tsv文件名}`, 共有{new_df.shape[0]}个话题')
    r2_path = r2.upload_to_r2_zhihu(tsv_str=tsv_text, filename=tsv文件名)
    return r2_path


if __name__ == '__main__':
    # 检测R2账号ID是否存在
    HAS_R2_CREDS = bool(r2.ACCOUNT_ID)
    if HAS_R2_CREDS:
        # 上传R2
        write_topic_r2()
    else:
        logger.info(f'环境变量HAS_R2_CREDS={HAS_R2_CREDS}, 没有保存')


#!jupyter nbconvert --to python --no-prompt --TemplateExporter.exclude_input_prompt=True --TemplateExporter.exclude_output_prompt=True  zhihu_hotsearch.ipynb




