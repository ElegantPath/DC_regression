# coding: utf-8
#   @file       check_phen.py
#   @details    python script
#   @author     11055
#   @data       2019/9/10 14:26

import os
import pandas as pd

from .interface_check import InterfaceCheck


class CheckPhen(InterfaceCheck):

    def __init__(self, *args, **kwargs):
        self.data = {}

        self.aggregate = kwargs['batch1']
        self.aggr_temp = self.aggregate.dropna(axis=0, how='all')
        self.norm_temp = kwargs['batch2']
        for i in kwargs.get('ignore', []):
            print(i)
            del self.aggr_temp[i]
            del self.norm_temp[i]
        self.keyList = list(self.aggr_temp.columns)

    #  match case in batch
    def match(self, suffixes=['', '_norm']):
        norm = self.norm_temp[self.keyList]
        df = pd.merge(self.aggr_temp, norm, how='inner', left_index=True, right_index=True, suffixes=suffixes)
        self.aggr = df[self.keyList]
        self.norm = df[[i + suffixes[1] for i in self.keyList]]
        self.norm.columns = self.keyList
        return df

    def compare(self) -> pd.DataFrame:
        aggr = self.aggr.reset_index()
        norm = self.norm.reset_index()
        df = pd.concat([aggr, norm])
        df.drop_duplicates(keep=False, inplace=True)
        df['index'] = [i.split('/')[-1] for i in df['index']]
        df = df.sort_values(by='index')
        return df

    def run(self) -> str:
        count_0 = len(self.match())
        res = self.compare()
        count_1 = count_0 - len(res) * 0.5
        res.sort_values('index', inplace=True)
        self.data['nData'] = res
        self.data['nPath'] = list(set(res['index']))

        string = f"""
--------CheckPhen

        运行病例数量：{len(self.aggregate)}
        生成数据数量：{len(self.aggr_temp)}
        标准结果数量：{len(self.norm_temp)}
        数据匹配数量：{count_0}
        检测通过数量：{count_1}
        
        """
        print(string)

    def summary(self):
        return self.compare()