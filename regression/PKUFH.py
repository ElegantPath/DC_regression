# coding: utf-8
#   @file       regression_PK_LYMPH_SUB.py
#   @details    python script
#   @author     11055
#   @data       2019/8/8 16:46

import json
import numpy as np
import pandas as pd
import os
import warnings

from .interface_collate import InterfaceCollate
from ..utility import read_log_res


class PKUFH_LYMPH_SUB(InterfaceCollate):
    PROPLIST = ['Lymph_0', 'CD3+_0', 'CD3+CD4+CD8+_0', 'CD3+CD4+CD8-_0', 'CD3+CD4-CD8+_0', 'CD3+CD4-CD8-_0', 'CD3-_0',
                'sum_0', 'Lymph_1', 'CD3+_1', 'CD3+CD16+CD56+_1', 'CD3-_1', 'CD3-CD16+CD56+_1', 'CD3-CD19+_1', 'sum_1']

    DTYPE = {'Lymph_0': np.float64,
             'CD3+_0': np.float64,
             'CD3+CD4+CD8+_0': np.float64,
             'CD3+CD4+CD8-_0': np.float64,
             'CD3+CD4-CD8+_0': np.float64,
             'CD3+CD4-CD8-_0': np.float64,
             'CD3-_0': np.float64,
             'sum_0': np.float64,
             'Lymph_1': np.float64,
             'CD3+_1': np.float64,
             'CD3+CD16+CD56+_1': np.float64,
             'CD3-_1': np.float64,
             'CD3-CD16+CD56+_1': np.float64,
             'CD3-CD19+_1': np.float64,
             'sum_1': np.float64}

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
        res = json.loads(logRes['ratio'])
        res = pd.Series(res, index=self.PROPLIST)
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

        res[self.PROPLIST] = res[self.PROPLIST].fillna(0).astype(np.float64)
        self.data['aggr'] = res
        self.data['prop'] = res[self.PROPLIST]

        if save:
            res.to_csv(self.config['aggrCsv'])

        return res

class PKUFH_6CTBNK(InterfaceCollate):
    PROPLIST = ['Bead', 'Lymph', 'CD3', 'CD8', 'CD4', 'CD48', 'CD16', 'CD19']

    DTYPE = {'Bead': np.float64,
             'Lymph': np.float64,
             'CD3': np.float64,
             'CD8': np.float64,
             'CD4': np.float64,
             'CD48': np.float64,
             'CD16': np.float64,
             'CD19': np.float64,}

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
        res = json.loads(logRes['ratio'])
        res = pd.Series(res, index=self.PROPLIST)
        res.name = int(os.path.realpath(dir).split('/')[-1][:4])
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
        res[self.PROPLIST] = res[self.PROPLIST].fillna(0).astype(np.float64)
        self.data['aggr'] = res
        self.data['prop'] = res[self.PROPLIST]

        if save:
            res.to_csv(self.config['aggrCsv'])

        return res