#!/usr/bin/env python
# coding: utf-8

# # r2_util
# 260619: 创建 

import os
import json
from datetime import datetime
import boto3
from botocore.config import Config
from botocore.errorfactory import ClientError 


__all__ = ['get_r2_client',
           'read_r2_tsv', 
           'file_exists_in_r2_weibo', 
           'upload_to_r2_weibo',
           'ACCOUNT_ID',
           'ACCESS_KEY_ID',
           'SECRET_ACCESS_KEY',
           'BUCKET_NAME',
           'RUN_ON_CI',
           ]


# 从环境变量读取密钥，不会硬编码进仓库
ACCOUNT_ID = os.getenv("ACCOUNT_ID","")
ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID", "")
SECRET_ACCESS_KEY = os.getenv("SECRET_ACCESS_KEY", "")
BUCKET_NAME = os.getenv("BUCKET_NAME", "")
RUN_ON_CI = os.getenv("RUN_ON_CI", "")


def get_r2_client():
    '''创建R2对象存储的S3客户端，用于上传和下载文件
    '''
    s3client = boto3.client(
        "s3",
        endpoint_url=f"https://{ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=SECRET_ACCESS_KEY,
        region_name="auto",
        config=Config(signature_version="s3v4")
    )
    return s3client


def read_r2_tsv(file_name):
    '''读取weibo目录下的tsv文件，返回原始文本字符串
    '''
    s3 = get_r2_client()
    # 前缀改为 weibo/，直接返回tsv文本
    key = f"weibo/{file_name}"
    resp = s3.get_object(Bucket=BUCKET_NAME, Key=key)
    content = resp["Body"].read().decode("utf-8")
    return content


def file_exists_in_r2_weibo(file_name: str) -> bool:
    """
    检查 weibo/ 目录下是否存在指定文件
    :param file_name: 文件名，如 "20260619_2221.json"
    :return: 存在返回True，不存在返回False
    """
    s3 = get_r2_client()
    key = f"weibo/{file_name}"
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=key)
        return True
    except ClientError as err:
        err_code = err.response["Error"]["Code"]
        # R2 文件不存在返回 404，标准S3是 NoSuchKey，两个都兼容
        if err_code in ("NoSuchKey", "404"):
            return False
        raise


def upload_to_r2_weibo(tsv_str:str, filename:str, debug:bool=False) -> str:
    '''上传TSV字符串到R2对象存储的data/目录下
    ''' 
    s3 = get_r2_client()
    file_key = f"weibo/{filename}"
    body_bytes = tsv_str.encode("utf-8")

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=file_key,
        Body=body_bytes,
        #ContentType="text/tab-separated-values", # 控制台不可预览  
        ContentType="text/plain"  # 改成plain，控制台可预览 
    )
    return file_key


if '__main__' == __name__:
    with open("data/wb_hottopic_20260619.tsv", "r", encoding="utf-8") as f:
       tsv_content = f.read()
    upload_to_r2_weibo(tsv_content, filename="wb_hottopic_20260619.tsv")


if '__main__' == __name__:
    tsv_text = read_r2_tsv("wb_hottopic_20260619.tsv")
    # 转 pandas DataFrame 查看
    import pandas as pd
    from io import StringIO
    df = pd.read_csv(StringIO(tsv_text), sep="\t").fillna('')
    df


if '__main__' == __name__:
    file_exists_in_r2_weibo("wb_hottopic_20260619.tsv")


if '__main__' == __name__:
    data = read_r2_tsv("wb_hottopic_20260619.tsv")
    print(data)


#!jupyter nbconvert --to python --no-prompt --TemplateExporter.exclude_input_prompt=True --TemplateExporter.exclude_output_prompt=True  r2_util.ipynb




