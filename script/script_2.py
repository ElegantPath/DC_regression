# coding: utf-8
#   @file       script_2.py
#   @details    python script
#   @author     11055
#   @data       2019/9/29 17:08

import numpy as np
import os
import pandas as pd

casePath = r"C:\Users\11055\Desktop\PK_LYMPH_SUB1"
fileList = ['细胞计数1.csv', '细胞计数2.csv', '单核细胞亚群.csv', '淋巴细胞亚群.csv', '粒细胞亚群.csv']


def parse(src):
    res = []
    for file in fileList[:1]:
        df = pd.read_csv(os.path.join(src, file), engine='python', encoding='utf8')
        temp_res = []
        for i in list(df.columns[1:]):
            temp = df[['Unnamed: 0', i]]
            temp['Unnamed: 0'] += f'-{i}'
            temp.columns = ['item', 1]
            temp_res.append(temp)
        res.append(pd.concat(temp_res))
    res = pd.concat(res)
    res.index = res['item']
    res = res[1].fillna(0)
    res.name = src
    return res


if __name__ == '__main__':
    casePath = r"C:\Users\11055\Desktop\PK_LYMPH_SUB1"
    fileList = ['细胞计数1.csv', '细胞计数2.csv', '单核细胞亚群.csv', '淋巴细胞亚群.csv', '粒细胞亚群.csv']
    res = []
    for dir in os.listdir(casePath):
        res.append(parse(os.path.join(casePath, dir)))
    res = pd.DataFrame(res)
    # res = res.reset_index(drop=True)
