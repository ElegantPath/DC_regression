# -*-coding:utf-8-*-
"""
@File     : XYS_6CTBNK.py
@Author   : jisi
@Email    : 16600208402@163.com
@Time     : 2020/7/21 16:17
@details  : python script
@status   : editing
"""

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


class XYS_6CTBNK(InterfaceCollate):
    PROPLIST = ['Beads %Parent', 'Lymphocyt %Parent', 'CD3+ %Parent', 'CD3+CD4+ %Parent', 'CD3+CD8+ %Parent',
                'CD19+ %Parent', 'CD3-CD16+CD56+ %Parent', 'CD3+CD16+CD56+ %Parent', 'num']

    DTYPE = {
        'Beads %Parent': np.float64,
        'Lymphocyt %Parent': np.float64,
        'CD3+ %Parent': np.float64,
        'CD3+CD4+ %Parent': np.float64,
        'CD3+CD8+ %Parent': np.float64,
        'CD19+ %Parent': np.float64,
        'CD3-CD16+CD56+ %Parent': np.float64,
        'CD3+CD16+CD56+ %Parent': np.float64,
        'num': np.float64
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
        res = json.loads(logRes['ratio'])
        res['num'] = logRes['number']
        res = pd.Series(res, index=self.PROPLIST)
        res.name = os.path.realpath(dir).replace('\\', '/').split('/')[-1][:5]
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

