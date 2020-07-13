# coding: utf-8
#  utility functions for fcmRegression class
#   @file       util_base.py
#   @author     Huanyu He
#   @data       2019-09-06


import codecs
import json
import os
import pandas as pd
import re
import shutil

from .util_exception import PathError


def createInstance(module_name, class_name, *args, **kwargs):
    moduleMeta = __import__(module_name, globals(), locals(), [class_name])
    classMeta = getattr(moduleMeta, class_name)
    obj = classMeta(*args, **kwargs)
    return obj


def pathCheck(src,isnew=False,level=0):
    if not os.path.exists(src):
        if isnew:
            if level == 0:
                ast = '/'.join(src.replace('\\', '/').split('/'))
            else:
                ast = '/'.join(src.replace('\\', '/').split('/')[:level])
            if not os.path.exists(ast):
                try:
                    os.makedirs(ast)
                except OSError:
                    raise PathError(f"<{src}> is error")
        else:    
            raise PathError(f"<{src}> not exist")
    return True


def read_log_text(logPath: str) -> str:
    logText = []
    try:
        with codecs.open(logPath, 'r', 'utf8') as f:
            for line in f:
                logText.append(line)
    except:
        with codecs.open(logPath, 'r', 'gbk') as f:
            for line in f:
                logText.append(line)
    return ''.join(logText)


def read_log_res(logPath: str, prefix='FCM_REGRESSION:', suffix=r'\$END') -> dict:
    logText = read_log_text(logPath)
    pattern = re.compile(f"{prefix}(.*){suffix}")
    resList = pattern.findall(logText)
    if len(resList):
        res = json.loads(resList[-1])
        return res



def intoRoman(tup):
    """
    (str,num) -> strRoman
    ('sa',2) -> 'saIII'
    :param tup:
    :return:
    """
    num = int(tup[1]) + 1
    res = ""
    roman = ["I", "V", "X", "L", "C", "D", "M"]
    j = 0
    while num:
        str_t = ""
        temp = num % 10
        if temp < 4:
            count = temp
            str_t += roman[j] * count
        elif temp == 4:
            str_t += roman[j]
            str_t += roman[j + 1]
        elif 5 <= temp <= 8:
            str_t += roman[j + 1]
            count = temp - 5
            str_t += roman[j] * count
        else:
            str_t += roman[j]
            str_t += roman[j + 2]
        res = str_t + res
        num //= 10
        j = j + 2
    return tup[0] + res

# def read_csv(csvPath):
# with codecs.open(logPath, 'r', 'utf-8') as f:
#     for line in f:
#         FCM = line.find('FCM_')
#         eq = line.find('=')
#         if (FCM >= 0) and (eq >= 0):
#             kwd = line[FCM:eq]
#             val = line[eq + 1:].strip()
#             if kwd in skipFCM:
#                 pass
#             elif kwd in fcmCD:
#                 rtd.setdefault(kwd, [])
#                 rtd[kwd] += list(val.split(','))
#             else:
#                 rtd.setdefault(kwd, []).append(val)
# return rtd


#  utility class for fcmRegression
# class fcmRegUtility(object):
#
#     @classmethod
#     # compare two log files
#     #  @param  log1    baseline CSV file
#     #  @param  log2    results CSV file
#     #  @return dictionary of different {key:value}
#     #  @see    parseResultsLog
#     @classmethod
#     def compareLog(cls, log1, log2):
#         fcm1 = cls.parseResultsLog(log1)
#         fcm2 = cls.parseResultsLog(log2)
#         diffDict = {}
#         for kwd in ('FCM_DIAG', 'FCM_ABNORMAL_GROUP'):
#             val1 = fcm1.get(kwd, [])
#             val2 = fcm2.get(kwd, [])
#             if val1 != val2:
#                 diffDict[kwd] = (val1, val2)
#
#         for kwd in ('FCM_STRONG_CD', 'FCM_POSITIVE_CD', 'FCM_DIM_CD',
#                     'FCM_NEGATIVE_CD',):
#             cds1 = set(fcm1.get(kwd, []))
#             cds2 = set(fcm2.get(kwd, []))
#             if cds1 != cds2:
#                 diffDict[kwd] = (list(cds1 - cds2), list(cds2 - cds1))
#         return diffDict
#
#     # generate a line of csv for a results.log file
#     #  @param  logPath file path for the results.log
#     #  @param  keyList default=None then use the class keyList.
#     #  @return a string of items in the keyList
#     #  @note   by default, truth comes from upper directory name
#     #  @see    parseResultsLog
#     @classmethod
#     def aggregateLog(cls, logPath, keyList=None):
#         res = cls.parseResultsLog(logPath)
#         if keyList == None:
#             keyList = cls.keyList
#         data = []
#         caseName = os.path.dirname(logPath).replace('\\', '/')
#         for key in keyList:
#             if key == 'case name':
#                 data.append(caseName)
#             elif key == 'truth':
#                 data.append(os.path.basename(os.path.dirname(caseName)))
#             elif key == 'FCM_DIAG':
#                 data.append(res.get(key, [''])[-1])
#             else:
#                 data.append(' '.join(res.get(key, [])))
#         return pd.Series(data, index=keyList)
#
#     # aggregate all results.log in the pathList
#     #  @details  call the aggregateLog to get a line of a single result
#     #  @param    pathList    list of paths to aggregate the results
#     #  @param    csvFile default=None
#     #  @param    keyList default=None, using class keyList
#     #  @param    ignoreList default=['ignore'], case insensitive
#     #  @param    resLog    default='FCM_results.log'
#     #  @return   DataFrame of aggregated results
#     #  @see      aggregateLog
#     @classmethod
#     def aggregateDir(cls, pathList, **kwargs):
#         keyList = kwargs.get('keyList', cls.keyList)
#         csvFile = kwargs.get('csvFile', None)
#         ignoreList = kwargs.get('ignoreList', ['ignore', ])
#         resLog = kwargs.get('resLog', 'FCM_results.log')
#
#         data = []
#         for path in pathList:
#             if not os.path.exists(path):
#                 print('cannot find path: %s, skipped' % path)
#                 continue
#             for r, _, files in os.walk(path):
#                 ignore = any(ign in r for ign in ignoreList)
#                 if not ignore and resLog in files:
#                     logPath = os.path.join(r, resLog)
#                     data.append(cls.aggregateLog(logPath, keyList))
#         data = pd.DataFrame(data)
#         if csvFile is not None:
#             data.fillna(-1).to_csv(csvFile, encoding='utf-8', index=0)
#         return data
#
#     # modify the inCSV to outCSV
#     #  @details    used for compare the aggregated results to baseline
#     #             in case of changed case name (path)
#     #  @param      inCSV   input CSV
#     #  @param      outCSV  outputCSV of modified case name
#     #  @param      refCSV  referenceCSV for changing/matching the case name
#     #  @param      key     default='case name'
#     #  @return     None
#     #  @note       other usage unknown
#     #  @see        aggregateCSV, aggregateDir, aggregate
#     @classmethod
#     def matchCSV(cls, inCSV, outCSV, refCSV, key='case name'):
#         data = pd.read_csv(inCSV, encoding='utf-8').fillna('')
#         ref = pd.read_csv(refCSV, encoding='utf-8').fillna('')
#
#         idx1 = data[key].isin(ref[key])
#         if not all(idx1):
#             caseMap = {}
#             idx2 = ~ref[key].isin(data[key])
#             for _, row in ref.loc[idx2].iterrows():
#                 case = os.path.basename(row[key])
#                 caseMap.setdefault(case, []).append(row[key])
#             for index, row in data.loc[~idx1].iterrows():
#                 case = os.path.basename(row[key])
#                 caseN = len(caseMap.setdefault(case, []))
#                 if caseN == 0:
#                     print('cannot find %s in refCSV' % case, refCSV)
#                 elif caseN == 1:
#                     data.loc[index, key] = caseMap[case][0]
#                 else:
#                     print('duplicate found %s in refCSV' % caseMap[case])
#         data.to_csv(outCSV, encoding='utf-8')
#
#     # compare two aggregate.csv file
#     #  @details    used for regression purpose
#     #  @param      agg1    old aggregated results
#     #  @param      agg2    new aggregated results
#     #  @param      filterList  list of strings for which to be included
#     #                         in the comparison
#     #  @return     DataFrame of different results
#     #  @note       case name (full path) should be exactly matching
#     #  @see        aggregateCSV, aggregateDir, aggregate
#     @classmethod
#     def compareResults(cls, agg1, agg2, filterList=None):
#         res1 = pd.read_csv(agg1, encoding='utf-8').fillna('')
#         res2 = pd.read_csv(agg2, encoding='utf-8').fillna('')
#         if filterList is not None:
#             def filter(res):
#                 IDX = []
#                 for index, row in res.iterrows():
#                     if any(key in row['case name'] for key in filterList):
#                         IDX.append(index)
#                 return res.loc[IDX]
#
#             res1 = filter(res1)
#             res2 = filter(res2)
#         name1 = os.path.basename(agg1)
#         name2 = os.path.basename(agg2)
#
#         idx1 = res1['case name'].isin(res2['case name'])
#         idx2 = res2['case name'].isin(res1['case name'])
#         res1 = res1.loc[idx1, :].sort_values('case name').reset_index(drop=True)
#         res2 = res2.loc[idx2, :].sort_values('case name').reset_index(drop=True)
#
#         diffIDX = res1['FCM_DIAG'] != res2['FCM_DIAG']
#         diff = res1.loc[diffIDX, ['case name', 'FCM_DIAG']].reset_index(drop=True
#                                                                         ).rename(columns={'FCM_DIAG': name1})
#         diff[name2] = res2.loc[diffIDX, 'FCM_DIAG'].values
#         diff['FCM_DIAG_WARNING'] = res2.loc[diffIDX, 'FCM_DIAG_WARNING'].values
#         print('%s %d, %s %d, compared %d, different %d'
#               % (name1, len(idx1), name2, len(idx2), sum(idx1), sum(diffIDX)))
#         return diff
#
#     # compare ratios in two aggregate.csv file
#     #  @details    used for regression purpose
#     #  @param      agg1    old aggregated results
#     #  @param      agg2    new aggregated results
#     #  @param      filterList  list of strings for which to be included
#     #                          in the comparison
#     #  @return     DataFrame of different results
#     #  @note       case name (full path) should be exactly matching
#     #  @see        aggregateCSV, aggregateDir, aggregate
#     @classmethod
#     def compareRatios(cls, agg1, agg2, filterList=None):
#         res1 = pd.read_csv(agg1, encoding='utf-8').fillna('')
#         res2 = pd.read_csv(agg2, encoding='utf-8').fillna('')
#
#         if filterList is not None:
#             def filter(res):
#                 IDX = []
#                 for index, row in res.iterrows():
#                     if any(key in row['case name'] for key in filterList):
#                         IDX.append(index)
#                 return res.loc[IDX]
#
#             res1 = filter(res1)
#             res2 = filter(res2)
#
#         idx1 = res1['case name'].isin(res2['case name'])
#         idx2 = res2['case name'].isin(res1['case name'])
#         res1 = res1.loc[idx1, :].sort_values('case name').reset_index(drop=True)
#         res2 = res2.loc[idx2, :].sort_values('case name').reset_index(drop=True)
#         ratioList = cls.ratioList
#         comparison = pd.concat([res1, res2[ratioList] - res1[ratioList]], axis=1)
#         columns = list(comparison.columns)
#         N = len(list(res1))
#         columns[N:] = ['diff ' + s for s in columns[N:]]
#         comparison.columns = columns
#         return comparison
#
#     # aggregate all results.log
#     #  @details    aggregate all results.log in the pathList
#     #                 defined in config
#     #  @param      None
#     #  @return     None
#     #  @note       pathList and aggregateCSV are required in config
#     def aggregate(self):
#         type(self).aggregateDir(self.config['pathList'],
#                                 resLog='FCM_results.log',
#                                 csvFile=self.config['aggregateCSV'],
#                                 ignoreList=self.config['ignoreList'],
#                                 keyList=self.config['keyList'])
#
#     # aggregate all baseline.log
#     #  @details    aggregate all baseline.log in the pathList
#     #             defined in config
#     #  @param      None
#     #  @return     None
#     #  @note       pathList and aggregateCSV are required in config
#     def aggregateBaseline(self):
#         type(self).aggregateDir(self.config['pathList'],
#                                 resLog='baseline.log',
#                                 csvFile=self.config['baselineCSV'],
#                                 ignoreList=self.config['ignoreList'],
#                                 keyList=self.config['keyList'])
#
#     # compare the aggregated results with baseline
#     #  @param  filterList  default=None, a list of strings
#     #                     for which to be included in the comparison
#     #  @return None
#     #  @note   aggregateCSV and baselineCSV are required in config
#     #  @see    compareResults
#     def compare(self, filterList=None):
#         aggregateCSV = self.config['aggregateCSV']
#         baselineCSV = self.config['baselineCSV']
#         if not os.path.exists(aggregateCSV):
#             print('cannot find aggregateCSV: %s' % aggregateCSV)
#             print('please run aggregate() or reset aggregateCSV in config')
#         if not os.path.exists(baselineCSV):
#             print('cannot find baselineCSV: %s' % baselineCSV)
#             print('please set valid baselineCSV in config')
#         return type(self).compareResults(baselineCSV, aggregateCSV, filterList)
#
#     # a utility function to use current FCM_results.log
#     #            as baseline.log
#     #  @param  None
#     #  @return None
#     def rebaseline(self):
#         resLog = 'FCM_results.log'
#         baseLog = 'baseline.log'
#         for path in self.config['pathList']:
#             if not os.path.exists(path):
#                 print('cannot find path: %s, skipped' % path)
#                 continue
#             for r, _, files in os.walk(path):
#                 if resLog in files:
#                     shutil.copy(os.path.join(r, resLog),
#                                 os.path.join(r, baseLog))
#
#     # does the row fit the diagType
#     #  @details    sort a row of aggregated CSV results into diagType
#     #              used in countRow to generate summary
#     #  @param      row   a row of DataFrame of an aggregated results
#     #  @param      diagType  diagnosis type
#     #  @return     True/False for a row whether belongs to a diagType
#     #  @note       'Total' is also a diagType, usually return True
#     #              should be re-implemented in inherited classes
#     #  @see        countRow
#     def sortRowType(self, row, diagType):
#         if diagType.lower() == 'total':
#             return True
#         else:
#             return False
#
#     # count a case (row) for summary
#     #  @details    analyze a single row from CSV file/pandas DataFrame
#     #              generate the count for diagType and 'Total', and others
#     #              assign a category to this row (case)
#     #  @param      row     a row of a DataFrame of an aggregated results
#     #  @return     a dictionary with key = 'truth' and value = Series
#     #  @note       Series should have the index of diagTypeList
#     #  @see        summarizeCSV, summarize
#     def countRow(self, row):
#         data = []
#         for diagType in self.config['diagTypeList']:
#             if self.sortRowType(row, diagType):
#                 data.append(1)
#             else:
#                 data.append(0)
#         return {row['truth']: pd.Series(data, index=self.config['diagTypeList'])}
#
#     # summarize the aggregated CSV results
#     #  @details    summarize the truth vs diagnoses for
#     #              all cases in the csv file
#     #  @param      csvFile     aggregated CSV result file
#     #  @param      filterList  a list of strings of which to be included
#     #  @return     DataFrame of a summary
#     #  @see        countRow, sortRowType
#     def summarizeCSV(self, csvFile, filterList=None):
#         data = pd.read_csv(csvFile, encoding='utf-8').fillna('')
#         report = {}
#         for index, row in data.iterrows():
#             if filterList is not None \
#                     and not any(key in row['case name'] for key in filterList):
#                 continue
#             count = self.countRow(row)
#             for truth in count:
#                 if truth in report:
#                     report[truth] += count[truth]
#                 else:
#                     report[truth] = count[truth]
#         return pd.DataFrame(report).transpose()
#
#     # summarize the aggregated results
#     #  @details    summarize the truth vs diagnoses
#     #              for all cases in the pathList
#     #  @param      filterList  a list of strings of which to be included
#     #  @return     DataFrame of a summary
#     #  @note       aggregateCSV should be defined in the config
#     #  @see        summarizeCSV
#     def summarize(self, filterList=None):
#         aggregateCSV = self.config['aggregateCSV']
#         if not os.path.exists(aggregateCSV):
#             print('cannot find aggregateCSV: %s' % aggregateCSV)
#             print('please run aggregate() or reset aggregateCSV in config')
#         else:
#             return self.summarizeCSV(aggregateCSV, filterList)
#
#     # filter the results
#     #  @details    find out in all results (within filterList)
#     #              for truth in truthList and diagType in diagList
#     #  @param      csvFile     aggregated CSV result file
#     #  @param      filterList  default=None, list of strings for case name
#     #  @param      truthList   default=None, list of truths
#     #  @param      diagTypeList default=None, list of diagTypes
#     #  @param      displayList  default=None, list of keywords
#     #                           to be displayed in the results
#     #  @param      *kwargs     row[k] == value
#     #  @return     DataFrame of itemized results
#     #  @see        countRow
#     def checkCSV(self, csvFile, **kwargs):
#         data = pd.read_csv(csvFile, encoding='utf-8').fillna('')
#         rowList = []
#         filterList = kwargs.get('filterList', None)
#         truthList = kwargs.get('truthList', None)
#         diagTypeList = kwargs.get('diagTypeList', None)
#         displayList = kwargs.get('displayList', None)
#
#         for index, row in data.iterrows():
#             if filterList is not None \
#                     and not any(key in row['case name'] for key in filterList):
#                 continue
#             if truthList is not None \
#                     and not any(key in row['truth'] for key in truthList):
#                 continue
#             if diagTypeList is not None:
#                 count = list(self.countRow(row).values())[0]
#                 if not any(count[key] > 0 for key in diagTypeList):
#                     continue
#
#             matched = True
#             for k in row.index:
#                 if k in kwargs and row[k] != kwargs[k]:
#                     matched = False
#                     break
#             if matched:
#                 if displayList is None:
#                     rowList.append(row)
#                 else:
#                     rowList.append(row[displayList])
#         return pd.DataFrame(rowList).reset_index(drop=True)
#
#     # filter the results
#     #  @details    find out in all results (within filterList)
#     #              for truth in truthList and diagType in diagList
#     #  @param      filterList  default=None, list of strings for case name
#     #  @param      truthList   default=None, list of truths
#     #  @param      diagTypeList default=None, list of diagTypes
#     #  @param      displayList  default=None, list of keywords
#     #                           to be displayed in the results
#     #  @param      *kwargs     row[k] == value
#     #  @return     DataFrame of itemized results
#     #  @see        checkCSV, countRow
#     def check(self, **kwargs):
#         aggregateCSV = self.config['aggregateCSV']
#         if not os.path.exists(aggregateCSV):
#             print('cannot find aggregateCSV: %s' % aggregateCSV)
#             print('please run aggregate() or reset aggregateCSV in config')
#         else:
#             return self.checkCSV(aggregateCSV, **kwargs)
