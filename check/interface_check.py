# coding: utf-8
#   @file       interface_check.py
#   @details    python script
#   @author     11055
#   @data       2019/9/9 16:02

from ..utility import *


class InterfaceCheck(object):

    def __init__(self, *args, **kwargs):

        self.data = {}
        self.aggr = None
        self.norm = None
        self.keyList = list(self.aggr.columns)

    def match(self, suffixes=['', '_norm']):

        norm = self.norm[self.keyList]
        df = pd.merge(self.aggr, norm, how='inner', left_index=True, right_index=True, suffixes=suffixes)
        return df

    def diff(self, drop=False):

        df = self.match(suffixes=['', '_diff'])
        for i in df:
            if '_diff' in i:
                df[i] = df[i[:-5]] - df[i]
        if drop:
            df = df[[i for i in df if '_diff' in i]]
        self.data['diff'] = df
        return df

    def compare(self):
        pass

    def summary(self):
        pass

    def run(self):
        pass
