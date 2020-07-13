# coding: utf-8
#  regression interface classes
#   @file       interface_collate.py
#   @details    define basic APIs
#   @author     Huanyu He, Zhang Lu
#   @data       2019-09-06

from copy import deepcopy
import os
import pandas as pd
import warnings

from ..utility import createInstance, pathCheck


class InterfaceCollate(object):

    DTYPE = 'object'

    FILENAME = 'FCM_results.log'

    def __init__(self, config):

        self.config = config

        self.execList = self.config.get('execList', [])

        self.checkList = []

        self.data = {}

        self.parse_config()

    def parse_config(self):

        if 'casePath' in self.config:
            path = self.config['casePath']
            if os.path.exists(path):
                for p, _, f in os.walk(path):
                    if self.FILENAME in f:
                        self.execList.append(p)
            else:
                warnings.warn(f"Can't find case in the path:{path}")

        if 'aggrCsv' in self.config:
            pathCheck(self.config['aggrCsv'], True, -1)


        if 'normCsv' in self.config and os.path.exists(self.config['normCsv']):
            if self.config['normCsv'].endswith('.csv'):
                self.data['norm'] = pd.read_csv(self.config['normCsv'], dtype=self.DTYPE, index_col=0)
            elif self.config['normCsv'].endswith('.xlsx'):
                if 'sheet_name' in self.config:
                    self.data['norm'] = pd.read_excel(self.config['normCsv'],dtype=self.DTYPE, index_col=0, sheet_name=self.config['sheet_name'])
                else:
                    self.data['norm'] = pd.read_excel(self.config['normCsv'],dtype=self.DTYPE, index_col=0)


        if 'resuCsv' in self.config and os.path.exists(self.config['normCsv']):
            self.data['resu'] = pd.read_csv(self.config['resuCsv'], dtype=self.DTYPE, index_col=0)

        if self.execList:
            self.execList = list(set(self.execList))
            self.execList.sort()
            for path in self.execList:
                if not os.path.exists(os.path.join(path, self.FILENAME)):
                    warnings.warn(f"No information file in the path:{path}")
                    self.execList.remove(path)

    def parse_check(self):

        for check in self.config.get('checkList', []):
            moduleName = check.get('moduleName')
            className = check.get('className')
            if moduleName is None or className is None:
                raise RuntimeError('Cannot find moduleName or className in check''s config: %s' % check)
            else:
                obj = createInstance(moduleName, className, *check.get('args', []), **check.get('kwargs', {}),
                                     **{k: deepcopy(self.data.get(v)) for k, v in check.get('data', {}).items()})
                self.checkList.append(obj)

    def parse_result(self, dir):

        pass

    def aggregate(self):
        
        pass

    def run(self):

        self.parse_check()
        [i.run() for i in self.checkList]
