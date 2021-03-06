# coding: utf-8
#   @file       check_conc.py
#   @details    python script
#   @author     11055
#   @data       2019/11/26 16:17


import os
import pandas as pd
import re

from .interface_check import *


class CheckPropPK1(InterfaceCheck):

    def __init__(self, *args, **kwargs):

        self.data = {}

        self.aggr = kwargs['batch1']
        self.norm = kwargs['batch2']
        self.norm.columns = [str(i) for i in self.norm]
        self.keyList = []
        self.comp = kwargs.get('comp',None)
        self.params = args
        self.parse()

    def parse(self):
        df = self.aggr
        df['3'] = (df['CD3+_0'] + df['CD3+_1']) / (df['Lymph_0'] + df['Lymph_1']) * 100
        df['4'] = (df['CD3+CD4+CD8+_0'] + df['CD3+CD4+CD8-_0']) / df['Lymph_0'] * 100
        df['8'] = (df['CD3+CD4+CD8+_0'] + df['CD3+CD4-CD8+_0']) / df['Lymph_0'] * 100
        df['16'] = df['CD3-CD16+CD56+_1'] / df['Lymph_1'] * 100
        df['19'] = df['CD3-CD19+_1'] / df['Lymph_1'] * 100
        self.aggr = df[['3', '4', '8', '16', '19']]
        self.keyList = [i for i in self.aggr]

    def match(self, suffixes=['', '_norm']) -> pd.DataFrame:

        return pd.merge(self.aggr, self.norm, how='inner', left_index=True, right_index=True, suffixes=suffixes)

    def diff(self, drop=False,suffixes=['', '_diff']) -> pd.DataFrame:

        df = self.match(suffixes=suffixes)
        for col in df:
            if '_diff' in col:
                df[col] = df[col[:-5]] - df[col]
        if drop:
            df = df[[i for i in df if '_diff' in i]]
        return df

    def compare(self):

        diff = self.diff(suffixes=['_diff', '']).apply(abs)

        if self.comp:
            for i in self.keyList:
                self.comp[i+'_diff'] = 1
            diff = diff.mul(pd.Series(self.comp),axis=1)
            for i in self.keyList:
                diff[i + '_diff'] = diff[i + '_diff'] > diff[i]
        else:
            px = self.params[0]
            py = self.params[1]
            pz = self.params[2]

            def fun(x):
                if x < px:
                    return x * py
                else:
                    return x * pz

            for i in self.keyList:
                diff[i] = [fun(x) for x in diff[i]]
                diff[i + '_diff'] = diff[i + '_diff'] > diff[i]

        return diff

    def run(self):
        df = self.compare()
        df = df[[i for i in df if '_diff' in i]]
        res = df.sum(axis=1)
        count_0 = len(df)
        count_1 = len(res[res == 0])
        self.data['nPath'] = list(res[res > 0].index)
        df = self.match()
        df = df[df.index.isin(self.data['nPath'])]
        self.data['nData'] = df

        string = f"""
--------CheckRatio
        标准结果数量：{len(self.norm)}
        生成数据数量：{len(self.aggr)} 
        数据匹配数量：{count_0}
        检测通过数量：{count_1}
        未通过的数量：{count_0 - count_1}
        检测通过rat：{count_1/count_0}
        """
        print(string)

    def summary(self,drop=True):
        return self.diff(drop=drop)

    def summary2(self):
        return self.compare()