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
        self.norm = kwargs['batch2'][list(self.aggr.columns)]
        self.params = args

    def match(self, suffixes=['', '_norm']) -> pd.DataFrame:

        return pd.merge(self.aggr, self.norm, how='inner', left_index=True, right_index=True, suffixes=suffixes)

    def diff(self, drop=False, suffixes=['', '_diff']) -> pd.DataFrame:

        df = self.match(suffixes=suffixes)
        for col in df:
            if '_diff' in col:
                df[col] = df[col[:-5]] - df[col]
        if drop:
            df = df[[i for i in df if '_diff' in i]]
        return df

    def run(self):

        diff = self.diff(suffixes=['_diff', '']).apply(abs)
        px = self.params[0]
        py = self.params[1]
        pz = self.params[2]

        diff['Lymph Events_diff'] = diff['Lymph Events_diff'] > diff['Lymph Events'] * px
        diff['CD3+_diff'] = diff['CD3+_diff'] > diff['CD3+'] * py
        for i in ['CD3+CD4+', 'CD3+CD8+', 'CD3+CD4+CD8+', 'CD16+CD56', 'CD19+']:
            diff[i + '_diff'] = diff[i + '_diff'] > diff[i] * pz

        df = self.match()
        idx = (df['%T-sum'] < 0) | (df['LymphSum'] < 90)
        df2 = diff[~idx][['Lymph Events_diff', 'CD3+_diff', 'CD3+CD4+_diff', 'CD3+CD8+_diff',
                          'CD3+CD4+CD8+_diff', 'CD16+CD56_diff', 'CD19+_diff']]
        res = df2.sum(axis=1)
        count_0 = len(diff)
        count_1 = sum(idx)
        count_2 = len(res[res == 0])
        self.data['nPath'] = list(res[res > 0].index)
        self.data['nData'] = df[df.index.isin(self.data['nPath'])]

        string = f"""
--------CheckRatio
        生成数据数量：{len(self.aggr)}
        标准结果数量：{len(self.norm)}
        数据匹配数量：{count_0}
        计数异常数量：{count_1}
        检测通过数量：{count_2}
        未通过的数量：{count_0 - count_2}
        """
        print(string)
