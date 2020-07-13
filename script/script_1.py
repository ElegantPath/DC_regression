# coding: utf-8
#   @file       script_1.py
#   @details    python script
#   @author     11055
#   @data       2019/9/13 16:23

import os
import pandas as pd

from ..regression import *
from ..utility import read_log_res

HELP = """

import fcm_regression as rg

sc = rg.Script1('CYTEK_TBNK',[120]])

sc.parse()

sc.run()

"""


class Script1(object):

    def __init__(self, panelStr, idList, src='/home/zhanglu2/Documents/regression/fcm_regression/norm'):
        self.panelStr = panelStr
        self.idList = idList
        self.normCsv = os.path.join(src, f"{panelStr}.csv")


    def parse(self, regressionPath='/home/zhanglu2/Documents/dpctweb/apps/static/fcsfiles'):
        caseIn = self.idList
        if isinstance(caseIn, str):
            caseIn = [caseIn]
        return [os.path.realpath(f'{regressionPath}/{i}') for i in caseIn]

    def run(self):
        case = globals()[self.panelStr]({})
        res = []
        for i in self.parse():
            if case.parse_result(i) is not None:
                res.append(case.parse_result(i))
        res = pd.DataFrame(res)
        df = pd.read_csv(self.normCsv, index_col=0)
        df.update(res)
        df.to_csv(self.normCsv)
        return res

    @staticmethod
    def help(*args, **kwargs):
        print(HELP)
