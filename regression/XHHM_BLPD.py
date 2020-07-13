# coding: utf-8
#   @file       XHHM_BLPD.py
#   @details    python script
#   @author     11055
#   @data       2019/8/30 15:27


import json
import numpy as np
import os
import pandas as pd
import warnings

from .interface_collate import InterfaceCollate
from ..utility import read_log_res


class XHHM_BLPD(InterfaceCollate):
    PROPLIST = ['LymphB',
                'LymphT',
                'OtherLymphT',
                'Others', 'ProB',
                'abnormal']

    PHENLIST = ['DIAGNOSIS_TYPE',
                'DIAGNOSIS_TEXT',
                'RATIO',
                'STRONG_CD_LIST',
                'POSITIVE_CD_LIST',
                'DIM_CD_LIST',
                'PARTIAL_CD_LIST',
                'NEGATIVE_CD_LIST',
                'WARNING',
                'CONCLUSION']

    DTYPE = {'LymphB': np.float64,
             'LymphT': np.float64,
             'OtherLymphT': np.float64,
             'Others': np.float64,
             'ProB': np.float64,
             'abnormal': np.float64,
             'DIAGNOSIS_TYPE': str,
             'DIAGNOSIS_TEXT': str,
             'RATIO': str,
             'STRONG_CD_LIST': str,
             'POSITIVE_CD_LIST': str,
             'DIM_CD_LIST': str,
             'PARTIAL_CD_LIST': str,
             'NEGATIVE_CD_LIST': str,
             'WARNING': str,
             'CONCLUSION': str}

    def parse_result(self, dir):

        logRes: dict = read_log_res(os.path.join(dir, self.FILENAME))

        res1 = pd.DataFrame(json.loads(logRes['ratio']))['% Total']
        res1 = res1.reindex(index=self.PROPLIST)
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
        res2.reindex(index=self.PHENLIST)
        res2['CONCLUSION'] = logRes['conclusion']
        res2.fillna('')

        res: pd.Series = pd.concat([res1, res2])
        res = res.reindex(index=self.PROPLIST + self.PHENLIST)
        res.name = os.path.basename(dir)

        return res

    def aggregate(self, save=False):

        temp = []
        for path in self.execList:
            temp2 = self.parse_result(path)
            if temp2 is None:
                warnings.warn(f"{path} exptable is error")
                continue
            temp.append(temp2)
        res = pd.DataFrame(temp)
        res = res.sort_index()

        res[self.PROPLIST] = res[self.PROPLIST].fillna(0).astype(np.float64)
        res[self.PHENLIST] = res[self.PHENLIST].fillna('-- --').astype(np.str)
        self.data['aggr'] = res
        self.data['prop'] = res[self.PROPLIST]
        self.data['phen'] = res[self.PHENLIST]

        if save:
            res.to_csv(self.config['aggrCsv'])
        return res
