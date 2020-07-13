# coding: utf-8
#   @file       check_conc_xh.py
#   @details    python script
#   @author     11055
#   @data       2019/9/16 11:48

import os
import pandas as pd
import re

from .interface_check import *


class CheckConcXh(InterfaceCheck):

    def __init__(self, *args, **kwargs):

        self.data = {}

        self.aggregate = kwargs['batch1']
        self.norm = kwargs['batch2']['DIAG']
        self.aggr = self.aggregate.dropna(axis=0, how='all')

    @staticmethod
    def parse(x):

        if isinstance(x, float):
            x = str(x)
            return 'Normal'
        if '未见明显表型异常' in x:
            return 'Normal'
        if u'疑似异常' in x:
            return 'Exception'
        elif u'疑似' in x and u'符合' not in x:
            return 'Warning'
        pattern = re.compile(u'[A-Za-z3-]+')
        res = pattern.findall(x)
        res = sorted(list(set(res)))
        if len(res) == 1:
            if res[0] == 'AUL':
                return 'AL-AUL'
            return res[0]
        if ['AML', 'B-ALL'] == res:
            return 'M-B'
        elif ['AML', 'T-ALL'] == res:
            return 'M-T'
        elif ['AML', 'M3'] == res or ['AML', 'AML-M3'] == res:
            return 'AML-M3'
        elif ['B-ALL', 'T-ALL'] == res:
            return 'T-B'
        else:
            return 'Complex'

    def match(self) -> pd.DataFrame:

        res = pd.merge(self.aggr, self.norm, how='inner', left_index=True, right_index=True, suffixes=['', '_norm'])
        return res

    def run(self) -> str:

        df = self.match()[['DIAG_norm', 'DIAG']]
        count_3 = len(df[df['DIAG'] == 'Exception'])
        df = df[df['DIAG_norm'] != df['DIAG']]

        count_0 = len(self.aggregate)
        count_1 = len(self.aggr)
        count_2 = count_1 - len(df)

        string = f"""
--------CheckDIAG

        运行病例数量：{count_0}
        生成数据数量：{count_1}
        检测通过数量：{count_2}
        检测通过比例：{round(count_2 * 1.0 / count_0, 4)}
        异常表型数量：{count_3}
        异常表型比例：{round(count_3 * 1.0 / count_0, 4)}
        
        """
        print(string)

    def summary(self) -> pd.DataFrame:

        df = self.match()[['DIAG_norm', 'DIAG']]
        df['DIAGNOSE TABLE'] = 1
        res = df.groupby(['DIAG_norm', 'DIAG']).count()
        res = res.unstack()
        return res.fillna(0)
