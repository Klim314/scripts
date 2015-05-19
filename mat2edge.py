#!/usr/bin/python3

#Takes two correlation matrices drawn from twoMAT and extracts values which meet thresholds
#format: ./twoMat.py <corMat> <pMat> <coreCut> <pCut>

import sys
import argparse


#File I/O
def readTsv(fileName):
	holder = []
	with open(fileName, 'r') as f:
		for i in f:
			holder.append(i.strip().split('\t'))
	return holder

def writeTsv(mat, fileName):
	length = len(mat)
	with open (fileName, 'w') as f:
		for lst in mat:
			f.write("\t".join(lst) + '\n')

#converters
def matStr2Flt(mat):
	for i in range(len(mat)):
		for j in range(len(mat[i])):
			if i != 0 and j != 0:
				mat[i][j] = float(mat[i][j])


#checker functions

def check(corMat, pMat, i, j, cCut, pCut):
	cVal = corMat[i][j] 
	pVal = pMat[i][j]
	#assumption, if corCut < 0, we're looking for the most negative
	if pVal > pCut:
		return False
	#deal with negatives
	if cCut < 0 and cVal < cCut:
		return True
	if cCut >=0 and cVal > cCut:
		return True
	return False



parser = argparse.ArgumentParser()
parser.add_argument("corMat", help= "correlation matrix from twoMat")
parser.add_argument("pMat", help= "pVal matrix from twoMat")
parser.add_argument("posCorCut", help= "correlation cutoff for positive values", type = float)
parser.add_argument("negCorCut", help= "correlation cutoff for negative values", type = float)
parser.add_argument("pCut", help= "pVal cutoff", type = float)
args = parser.parse_args()

#system arguments
corMat = args.corMat
posCorCut = args.posCorCut
negCorCut = -args.negCorCut
pMat = args.pMat
pCut = args.pCut

[print(i) for i in [corMat,posCorCut, negCorCut, pMat, pCut]]

corMat = readTsv(corMat)
pMat = readTsv(pMat)
matStr2Flt(corMat)
matStr2Flt(pMat)

resLst, posResLst, negResLst = [],[],[]

###for all numerical values
for i in range(1,len(corMat)):
	for j in range(1, len(corMat[0])):
		print ("comparing: ", corMat[i][j], pMat[i][j])
		#check negative
		if check(corMat, pMat, i ,j, negCorCut, pCut):
			
			negResLst.append((corMat[0][j], pMat[i][0], corMat[i][j], pMat[i][j], '-' ))
			resLst.append((corMat[0][j], pMat[i][0], corMat[i][j], pMat[i][j], '-' ))
		elif check(corMat, pMat, i ,j, posCorCut, pCut):
			print("pos")
			posResLst.append((corMat[0][j], pMat[i][0], corMat[i][j], pMat[i][j], '+' ))
			resLst.append((corMat[0][j], pMat[i][0], corMat[i][j], pMat[i][j], '+' ))
		else:
			print("NONE")
			print(negCorCut, pCut)

with open (".".join([args.corMat[4:-4], str(posCorCut) + '_' + str(negCorCut) + '-' + str(pCut), "extracts.out"]), 'w') as f:
	for i in resLst:
		i = map(str, i)
		f.write("	".join(i) + "\n")

with open (".".join([args.corMat[4:-4], str(negCorCut) + '-' + str(pCut), "neg_extracts.out"]), 'w') as f:
	for i in negResLst:
		i = map(str, i)
		f.write("	".join(i) + "\n")

with open (".".join([args.corMat[4:-4], str(posCorCut) + '-' + str(pCut), "pos_extracts.out"]), 'w') as f:
	for i in posResLst:
		i = map(str, i)
		f.write("	".join(i) + "\n")