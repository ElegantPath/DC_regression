# coding: utf-8
#   @file       check_prop.py
#   @details    python script
#   @author     11055
#   @data       2019/9/9 9:58

import pandas as pd

from .interface_check import InterfaceCheck


class CheckProp(InterfaceCheck):

    def __init__(self, *args, **kwargs):

        self.data = {}

        self.aggr = kwargs['batch1']
        self.norm = kwargs['batch2']
        self.comp = kwargs.get('comp',None)
        self.keyList = list(self.aggr.columns)
        self.params = args

    def match(self, suffixes=['', '_norm']) -> pd.DataFrame:

        norm = self.norm[self.keyList]
        return pd.merge(self.aggr, norm, how='inner', left_index=True, right_index=True, suffixes=suffixes)

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
