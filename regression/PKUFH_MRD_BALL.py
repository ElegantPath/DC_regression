# coding: utf-8
#   @file       PKUFH_MRD_BALL.py
#   @details    python script
#   @author     11055
#   @data       2019/8/13 15:29


import json
import numpy as np
import os
import pandas as pd
import warnings

from .interface_collate import InterfaceCollate
from ..utility import read_log_res


class PKUFH_MRD_BALL(InterfaceCollate):
    PROPLIST = [
        'Others',
        'Non-B-Lym',
        'CD19+',
        'ProB',
        'PreB',
        'EarlyB',
        'ImmatureB',
        'MatureB',
        'Plasma',
        'Non-Specific',
        'abnor-1',
        'abnor-2',
        'abnor-3',
        'abnor-4',
        'abnor-13',
        'abnor-58',
        'abnor-45'
    ]
    PHENLIST = ['DIAGNOSIS_TYPE',
                'DIAGNOSIS_TEXT',
                'RATIO',
                'STRONG_CD_LIST',
                'POSITIVE_CD_LIST',
                'DIM_CD_LIST',
                'PARTIAL_CD_LIST',
                'NEGATIVE_CD_LIST',
                'CONCLUSION']

    DTYPE = {'Others': np.float64,
             'Non-B-Lym': np.float64,
             'CD19+': np.float64,
             'ProB': np.float64,
             'PreB': np.float64,
             'EarlyB': np.float64,
             'ImmatureB': np.float64,
             'MatureB': np.float64,
             'Plasma': np.float64,
             'Non-Specific': np.float64,
             'abnor-1': np.float64,
             'abnor-2': np.float64,
             'abnor-3': np.float64,
             'abnor-4': np.float64,
             'abnor-13': np.float64,
             'abnor-58': np.float64,
             'abnor-45': np.float64,
             'DIAGNOSIS_TYPE': np.str,
             'DIAGNOSIS_TEXT': np.str,
             'RATIO': np.str,
             'np.strONG_CD_LIST': np.str,
             'POSITIVE_CD_LIST': np.str,
             'DIM_CD_LIST': np.str,
             'PARTIAL_CD_LIST': np.str,
             'NEGATIVE_CD_LIST': np.str,
             'CONCLUSION': np.str}

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
        res1 = df1['% Total']
        res1 = res1.fillna(0)

        res2 = logRes['phenotype'][0]
        for i in res2:
            if isinstance(res2[i], list):
                if len(res2[i]):
                    res2[i].sort()
                    res2[i] = ','.join(res2[i])
                else:
                    res2[i] = '-- --'
        res2 = pd.Series(res2)
        res2['CONCLUSION'] = logRes['conclusion']

        res: pd.Series = pd.concat([res1, res2])
        res = res.reindex(index=self.PROPLIST + self.PHENLIST)
        res.name = os.path.realpath(dir)
        return res

        #  API to aggregate case results

    def aggregate(self, save=False):
        res = []
        for path in self.execList:
            temp = self.parse_result(path)
            if temp is None:
                warnings.warn(f"{path} log is error")
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
