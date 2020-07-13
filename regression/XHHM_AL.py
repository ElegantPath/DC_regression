# coding: utf-8
#   @file       XHHM_AL.py
#   @details    python script
#   @author     11055
#   @data       2019/9/19 13:39


import json
import numpy as np
import os
import pandas as pd
import re
import warnings

from .interface_collate import InterfaceCollate
from ..utility import read_log_res


class XHHM_AL(InterfaceCollate):
    PROPLIST = ['debris',
                'Others',
                'Lymph',
                'ProB',
                'Myel',
                'NRBC',
                'Mono',
                'Granu',
                'abnor-1',
                'abnor-2',
                'abnor-3',
                'abnor-4'
                ]
    PHENLIST = [
        'DIAGNOSIS_TYPE',
        'DIAGNOSIS_TEXT',
        'RATIO',
        'STRONG_CD_LIST',
        'POSITIVE_CD_LIST',
        'DIM_CD_LIST',
        'PARTIAL_CD_LIST',
        'NEGATIVE_CD_LIST',
        'CONCLUSION']

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
             'DIAGNOSIS_TYPE': str,
             'DIAGNOSIS_TEXT': str,
             'RATIO': str,
             'STRONG_CD_LIST': str,
             'POSITIVE_CD_LIST': str,
             'DIM_CD_LIST': str,
             'PARTIAL_CD_LIST': str,
             'NEGATIVE_CD_LIST': str,
             'CONCLUSION': str}

    def parse_result(self, dir: str) -> object:
        """
        1.根据日志文件中细胞比例生成row
        :param dir:
        :return:
        """
        file = os.path.join(dir, self.FILENAME)
        logRes = read_log_res(file)
        if logRes is None:
            return

        df1 = pd.DataFrame(json.loads(logRes['ratio']))
        res1 = df1['Total']
        res1 = res1 / res1.sum()
        res1 = res1.reindex(index=self.PROPLIST)
        res1 = res1.fillna(0)

        if len(logRes['phenotype']):
            res2 = logRes['phenotype'][0]
            for i in res2:
                if isinstance(res2[i], list):
                    if len(res2[i]):
                        res2[i].sort()
                        res2[i] = ','.join(res2[i])
                    else:
                        res2[i] = '-- --'
            res2 = pd.Series(res2)
            res2.reindex(index=self.PHENLIST)
            res2['CONCLUSION'] = logRes['conclusion']
        else:
            res2 = pd.Series({}, index=self.PHENLIST)
            res2['CONCLUSION'] = logRes['conclusion']

        res: pd.Series = pd.concat([res1, res2])
        res = res.reindex(index=self.PROPLIST + self.PHENLIST)
        res.name = os.path.realpath(dir)
        return res

    def aggregate(self, save=False):

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

        res = []
        for path in self.execList:
            temp = self.parse_result(path)
            if temp is None:
                warnings.warn(f"{path} log is error")
                continue
            res.append(temp)
        res = pd.DataFrame(res)
        res.sort_index(inplace=True)
        res['DIAG'] = [parse(i) for i in res['CONCLUSION']]

        res[self.PROPLIST] = res[self.PROPLIST].fillna(0).astype(np.float64)
        res[self.PHENLIST] = res[self.PHENLIST].fillna('-- --').astype(np.str)
        self.data['aggr'] = res
        self.data['prop'] = res[self.PROPLIST]
        self.data['phen'] = res[self.PHENLIST]

        if save:
            res.to_csv(self.config['aggrCsv'])
        return res
