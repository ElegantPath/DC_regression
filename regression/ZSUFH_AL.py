# coding: utf-8
#   @file       ZSUFH_AL.py
#   @details    python script
#   @author     11055
#   @data       2019/10/8 10:21

import json
import numpy as np
import pandas as pd
import os
import warnings

from .interface_collate import InterfaceCollate
from ..utility import read_log_res


class ZSUFH_AL(InterfaceCollate):
    PROPLIST = ['debris', 'Others', 'Lymph', 'ProB', 'Myel', 'NRBC', 'Mono', 'Granu', 'abnor-1',
                'abnor-2', 'abnor-3', 'abnor-4']

    PHENLIST = ['CD117 dist', 'CD34 dist', 'CD38 dist', 'CD45 dist', 'HLA-DR dist', 'CD16 dist', 'CD11b dist',
                'CD13 dist', 'CD33 dist', 'CD15 dist', 'CD64 dist', 'CD14 dist', 'CD5 dist', 'CD10 dist', 'CD19 dist',
                'CD20 dist', 'CD22 dist', 'CD4 dist', 'CD7 dist', 'CD56 dist', 'CD2 dist', 'CD8 dist', 'CD3 dist',
                'MPO dist', 'cCD3 dist', 'CD79a dist']
    CONCLIST = ['WARNINGS', 'RATIO', 'CONCLUSION']

    DTYPE = {'debris': np.float64,
             'Others': np.float64,
             'Lymph': np.float64,
             'ProB': np.float64,
             'Myel': np.float64,
             'NRBC': np.float64,
             'Mono': np.float64,
             'Granu': np.float64,
             'abnor-1': np.float64,
             'abnor-2': np.float64,
             'abnor-3': np.float64,
             'abnor-4': np.float64,
             '诊断结果': str,
             '异常细胞群占比%': str,
             'CD117 dist': str,
             'CD34 dist': str,
             'CD38 dist': str,
             'CD45 dist': str,
             'HLA-DR dist': str,
             'CD16 dist': str,
             'CD11b dist': str,
             'CD13 dist': str,
             'CD33 dist': str,
             'CD15 dist': str,
             'CD64 dist': str,
             'CD14 dist': str,
             'CD5 dist': str,
             'CD10 dist': str,
             'CD19 dist': str,
             'CD20 dist': str,
             'CD22 dist': str,
             'CD4 dist': str,
             'CD7 dist': str,
             'CD56 dist': str,
             'CD2 dist': str,
             'CD8 dist': str,
             'CD3 dist': str,
             'MPO dist': str,
             'cCD3 dist': str,
             'CD79a dist': str,
             'WARNINGS': str}

    def parse_result(self, dir: str) -> object:
        """
        1.根据日志文件中细胞比例生成row
        :param dir:
        :return:
        """

        def conclusion_parser(conc):
            if '符合急性髓系(AML)白血病表型' in conc:
                return 'AML'
            elif '符合急性B淋巴母细胞白血病表型' in conc:
                return 'B-ALL'
            elif '未见明显异常表达' == conc:
                return 'NORMAL'
            return conc

        file = os.path.join(dir, self.FILENAME)
        logRes = read_log_res(file)
        if logRes is None:
            return

        df1 = pd.DataFrame(json.loads(logRes['ratio']))
        df1['Events_1'] = df1['Events_1'].astype(np.float64)
        res1 = round(df1['Events_1'] / df1['Events_1'].sum(), 4)
        res1 = res1.fillna(0.000)

        res2 = logRes['phenotype'][0]
        for i in ['STRONG_CD_LIST', 'POSITIVE_CD_LIST', 'DIM_CD_LIST', 'PARTIAL_CD_LIST', 'NEGATIVE_CD_LIST']:
            for j in res2[i]:
                res2[j + ' dist'] = i[:3]
        res2 = pd.Series(res2)
        if len(logRes['warning']):
            res2['WARNING'] = ','.join(logRes['warning'])
        else:
            res2['WARNING'] = '-- --'
        res2['CONCLUSION'] = conclusion_parser(logRes['conclusion'])

        res: pd.Series = pd.concat([res1, res2])
        res = res.reindex(index=self.PROPLIST + self.PHENLIST + self.CONCLIST)
        res.name = os.path.realpath(dir)
        return res

    def aggregate(self, save=False):
        res = []
        for path in self.execList:
            temp = self.parse_result(path)
            if temp is None:
                warnings.warn("%s log is error" % path)
                continue
            res.append(temp)
        res = pd.DataFrame(res)
        res.sort_index(inplace=True)

        res[self.PROPLIST] = res[self.PROPLIST].fillna(0).astype(np.float64)
        res[self.PHENLIST] = res[self.PHENLIST].fillna('-- --').astype(np.str)
        self.data['aggr'] = res
        self.data['prop'] = res[self.PROPLIST]
        self.data['phen'] = res[self.PHENLIST]

        if save:
            res.to_csv(self.config['aggrCsv'])
        return res
