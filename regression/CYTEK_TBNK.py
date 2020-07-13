# coding: utf-8
#   @file       CYTEK_TBNK.py
#   @details    python script
#   @author     11055
#   @data       2019/10/23 9:37


import json
import numpy as np
import pandas as pd
import os
import warnings

from .interface_collate import InterfaceCollate
from ..utility import read_log_res


class CYTEK_TBNK(InterfaceCollate):

    PROPLIST = ['Ab_Debris', 'Ab_Others', 'Ab_CD3-CD16-CD19-', 'Ab_CD3+CD4-CD8-',
                 'Ab_CD3+CD4+CD8-', 'Ab_CD3+CD4-CD8+', 'Ab_CD3+CD4+CD8+', 'Ab_CD3-CD16+CD56+', 'Ab_CD3+CD16+CD56+',
                 'Ab_CD3-CD19+']
    PROPLIST2 = ['Lymph Events', 'CD3+', 'CD3+CD4+', 'CD3+CD8+', 'CD3+CD4+CD8+', 'CD3-', 'CD16+CD56', 'CD19+',
                '%T-sum', 'CD4/CD8 Ratio', 'LymphSum']

    DTYPE = {'Lymph Events': np.float64,
             'CD3+': np.float64,
             'CD3+CD4+': np.float64,
             'CD3+CD8+': np.float64,
             'CD3+CD4+CD8+': np.float64,
             'CD3-': np.float64,
             'CD16+CD56': np.float64,
             'CD19+': np.float64,
             '%T-sum': np.float64,
             'CD4/CD8 Ratio': np.float64,
             'LymphSum': np.float64,
             'Ab_debris': np.float64,
             'Ab_Others': np.float64,
             'Ab_CD3-CD16-CD19-': np.float64,
             'Ab_CD3+CD4-CD8-': np.float64,
             'Ab_CD3+CD4+CD8-': np.float64,
             'Ab_CD3+CD4-CD8+': np.float64,
             'Ab_CD3+CD4+CD8+': np.float64,
             'Ab_CD3-CD16+CD56+': np.float64,
             'Ab_CD3+CD16+CD56+': np.float64,
             'Ab_CD3-CD19+': np.float64
             }

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
        res1 = json.loads(logRes['ratio1'])
        res1 = pd.DataFrame(res1)['Percent']

        res2 = json.loads(logRes['ratio2'])
        res2 = pd.DataFrame(res2)[' ']

        res3 = json.loads(logRes['ratio3'])
        res3 = pd.DataFrame([res3]).T.iloc[:,0]
        res3 = res3 * 100
        res3.index = ['Ab_'+i for i in res3.index]

        res = pd.concat([res1, res2, res3]).astype(np.float64)
        res = res.reindex(index=self.PROPLIST+self.PROPLIST2)
        res.name = os.path.realpath(dir)
        return res.fillna(0)

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

        res[self.PROPLIST+self.PROPLIST2] = res[self.PROPLIST+self.PROPLIST2].fillna(0).astype(np.float64)
        self.data['aggr'] = res
        self.data['prop'] = res[self.PROPLIST]
        self.data['prop2'] = res[self.PROPLIST2]

        if save:
            res.to_csv(self.config['aggrCsv'])

        return res
