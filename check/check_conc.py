# coding: utf-8
#   @file       check_conc.py
#   @details    python script
#   @author     11055
#   @data       2019/10/22 16:17


import os
import pandas as pd
import re

from .interface_check import *


class CheckConc(InterfaceCheck):

    def __init__(self, *args, **kwargs):

        self.data = {}

        self.aggr = kwargs['batch1'][['CONCLUSION']]
        self.norm = kwargs['batch2'][['CONCLUSION']]

    def match(self) -> pd.DataFrame:

        res = pd.merge(self.aggr, self.norm, how='left', left_index=True, right_index=True, suffixes=['', '_NORM'])
        return res

    def run(self) -> str:

        df = self.match()[['CONCLUSION', 'CONCLUSION_NORM']]
        df.columns = ['DIAG', 'NORM']
        count_3 = len(df[df['DIAG'] == 'Exception'])
        df['RESULT'] = df['NORM'] == df['DIAG']
        self.data['RESULT'] = df

        count_1 = len(self.aggr)
        count_2 = df['RESULT'].sum()

        string = f"""
--------CheckDIAG

        生成数据数量：{count_1}
        检测通过数量：{count_2}
        检测通过比例：{round(count_2 * 1.0 / count_1, 4)}
        异常表型数量：{count_3}
        异常表型比例：{round(count_3 * 1.0 / count_1, 4)}

        """
        print(string)

    def summary(self) -> pd.DataFrame:

        df = self.match()[['CONCLUSION', 'CONCLUSION_NORM']]
        df.columns = ['DIAG', 'NORM']
        df['DIAGNOSE TABLE'] = 1
        res = df.groupby(['NORM', 'DIAG']).count()
        res = res.unstack()
        return res.fillna(0)

    def summary2(self) -> pd.DataFrame:

        return self.data['RESULT']
