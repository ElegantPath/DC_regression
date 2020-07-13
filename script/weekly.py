# coding: utf-8
#   @file       weekly.py
#   @details    python script
#   @author     11055
#   @data       2019/8/30 9:37

import os
import sys
import time
import warnings
import pandas as pd
from operator import methodcaller
from multiprocessing import Pool

warnings.filterwarnings("ignore")
sys.path.append(r'C:\Users\11055\Documents\fcm_lymph_sub')
import fcm_lymph_sub as fcm

config = {'casePath': "",
          'workDir': "",
          'panel': ""}


def run_multi_process(conf: dict, path: str) -> None:
    def runPanel(pT, dP):
        fcm.checkFCMCaseInDir(pT, dP, True)
        print('_(:з」∠)_Done %s %s' % (path, panelType))

    panelType = conf['panel']
    pathList = []
    for a, _, i in os.walk(path):
        if '.lmd' in i or '.fcs' in i:
            pathList.append(a)
    pathList = list(set(pathList))
    pool = Pool(processes=len(pathList) % 10 + 5)

    # main loop
    for path in pathList:
        pool.apply_async(runPanel, (panelType, path))

    pool.close()
    pool.join()
    print("Done")


def compare_indifference(conf: dict, visi: bool = False) -> pd.DataFrame or None:
    case = methodcaller(f"reg_{conf['panel']}")(conf)
    case.norm_read(os.path.join(conf['workDir'], 'last.csv'))
    os.rename(os.path.join(conf['workDir'], 'last.csv'),
              os.path.join(conf['workDir'], f"last{time.strftime('%y%m%d', time.localtime())}.csv"))
    case.generateCSV()
    case.compareRatio()
    case.summarizeCSV()

    if visi:
        writer = pd.ExcelWriter(f"rg{time.strftime('%y%m%d', time.localtime())}.xlsx")
        case.data['curr'].to_excel(writer, sheet_name='curr')
        case.data['norm'].to_excel(writer, sheet_name='norm')
        case.data['diff'].to_excel(writer, sheet_name='diff')
        if isinstance(case.data['summ'], list):
            for i in range(case.data['summ']):
                case.data['summ'][i].to_excel(writer, sheet_name=f'summ{i}')
        else:
            case.data['summ'].to_excel(writer, sheet_name=f'summ')
        writer.save()
        writer.close()

    case.data['curr'].to_csv(os.path.join(conf['workDir'], 'last.csv'))
    diff: pd.DataFrame = case.data['diff']
    diff_col = [i for i in list(diff.columns) if '_diff' in i]
    res = diff[((diff[diff_col] == 0).sum(axis=1)) != len(diff_col)]
    if len(res):
        return res


def mail() -> None:
    pass


if __name__ == "__main__":
    run_multi_process()
    compare_indifference(config)
    # mail()
