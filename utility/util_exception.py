# coding: utf-8
#   @file       util_exception.py
#   @details    python script
#   @author     11055
#   @data       2019/8/29 9:58

class PathError(Exception):
	def __init__(self,args):
		self.args = args
		# print(args[0])

# class ExceConfig(Exception):
#     pass


# class ExceRegression(Exception):
#     pass


# class Excecheck(Exception):
#     pass
