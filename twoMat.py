#!/usr/bin/env python3

#Takes [ij] an (i by k) and a (j by k) and creates a (j by i) matrix 
#matrices are in tsv format
#individual values consist of pairwise correlations of rows from i and j
#TODO: force output to separate output folder

import multiprocessing
import math 
import copy
from scipy.stats.stats import pearsonr
from scipy.stats import spearmanr
from time import strftime
import sys, argparse

#############
# FUNCTIONS #
#############

# helper functions
def lPrint(lst):
	for i in lst:
		print(i)

# IO functions
def readTsv(fileName):
	holder = []
	with open(fileName, 'r') as f:
		for i in f:
			holder.append(i.strip().split('\t'))
	return holder

def writeTSV(mat, fileName):
	length = len(mat)
	with open (fileName, 'w') as f:
		for lst in mat:
			f.write("\t".join(lst) + '\n')

#Whole Matrix Operators

##datatype converters
def matStr2Int(mat):
	for i in range(len(mat)):
		for j in range(len(mat[i])):
			if i != 0 and j != 0:
				mat[i][j] = int(mat[i][j])

def matInt2Str(mat):
	for i in range(len(mat)):
		for j in range(len(mat[i])):
			if i != 0 and j != 0:
				mat[i][j] = str(mat[i][j])

def matLog(mat, base = 2):
	for i in range(len(mat)):
		for j in range(len(mat[i])):
			if i != 0 and j != 0:
				mat[i][j] = math.log(mat[i][j] +1,base)

#################
#Argument setup #
#################

parser = argparse.ArgumentParser()
parser.add_argument("im1", help= "First input matrix")
parser.add_argument("im2", help= "Second input matrix")
parser.add_argument("-c", "--cores", help= "Number of cores to use (default 4)", type = int, default = 4)
parser.add_argument("-l", "--log", help= "Log transform the data with base X", type = int)
parser.add_argument("-r", "--rcoeff", help= "Determine coefficient. 1 = pearsonr, 2 = spearmanr. Currently buggy, assign manually.", type = int, default = 1)
parser.add_argument("-o", "--out", help= "fix an output name")
parser.add_argument("-p", help= "prepend on to output name")
parser.add_argument("-gc", "--getcounts", nargs = 2, metavar = ("RCUT", "PCUT"), help= "Get raw count data. rCutoff, pCutoff", type = float)
args = parser.parse_args()

#individual argument conditons
if args.cores:
	cores = args.cores
if args.getcounts:
	#r and p value cutoffs
	rCutoff = args.getcounts[0]
	pCutoff = args.getcounts[1]


if args.rcoeff:
	if args.rcoeff == 1: 
		rFunct = pearsonr
	elif args.rcoeff == 2:
		rFunct = spearmanr
if args.out:
	name = args.out

else:
	name = strftime("%Y-%m-%d-%H_%M") + ".out"
	if args.getcounts:
		countName = '_r' + str(rCutoff) + '_p' + str(pCutoff)+ '_' + name
	if args.p:
		name = args.p + "_" + name
		if args.getcounts:
			countName = args.p + "_" + countName



####################
# Initial Data Prep#
####################

# Read in all specified files
first = readTsv(args.im1)
second = readTsv(args.im2)

# Working copies of initial matrices
wFirst = copy.deepcopy(first)
wSecond = copy.deepcopy(second)

# convert from string to int
matStr2Int(wFirst)
matStr2Int(wSecond)

#log conversion | -l/ --log flag
if args.log:
	matLog(wFirst, args.log)
	matLog(wSecond, args.log)

#Main processing Loop
#row1 refers to mat1, row2 to mat2
def worker(row1, row2):
	#print("Running :", row1, " | ", row2)
	print(row1, "|", row2)
	print(wFirst[row1][1:])
	print(wSecond[row2][1:])
	value = pearsonr(wFirst[row1][1:], wSecond[row2][1:])
	return(row1, row2, value)

# All rows to be processed by workers
runs = [(i,j) for i in range(1, len(wFirst)) for j in range(1,len(wSecond))]
pool = multiprocessing.Pool(cores)
mappedRuns = pool.starmap(worker, runs)

# Empty Result table for insertion
corResult = [[i[0] for i in wFirst]]
for i in wSecond[1:]:
	corResult.append([i[0]] + [0 for j in range(len(wFirst)-1)])
pResult = copy.deepcopy(corResult)

try:
	#check if raw count data is neeeded. Store in countHolder
	if args.getcounts:
		countHolder = [[i for i in first[0]]]
		
	#Compilation of individual multiprocessed datasets
	for i in mappedRuns:
		corResult[i[1]][i[0]] = i[2][0]
		pResult[i[1]][i[0]] = i[2][1]
		if args.getcounts:
			if abs(i[2][0]) > rCutoff and i[2][1]< pCutoff:
				countHolder.append([first[i[0]][j] + "\t" + second[i[1]][j] for j in range(len(first[0]))])

except IndexError:
	print("ERROR")
	print (i);
	if i[0]:
		print(wFirst[i[0]])
	if i[1]:
		print(wSecond[i[1]])


#output
matInt2Str(corResult)
matInt2Str(pResult)

if args.getcounts:
	print("-------Writing Counts--------")
	writeTSV(countHolder, "counts_" + countName) #quickhack
print ("-------Writing Cor--------")
writeTSV(corResult, "cor_" +name)
print("-------Writing pVal--------")
writeTSV(pResult, "pval_" +name)
