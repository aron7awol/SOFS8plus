#oledpatchsortSOFS8+
#Enhancements by aron7awol based on original version:
#oledpatchsortSOFS8
#(c)2022 Auvien Limited, all rights reserved
#Thanks to AVS @PencilGeek for some range mods
#version 0.6
#https://www.avsforum.com/threads/lg-oleds-3d-lut-profiling-using-lightspace-thread.3043520/page-87#post-61434336

import sys
import csv
import operator
from operator import attrgetter
import random

verstring="SOFS8+"

m1inv = 16384 / 2610.0
m2inv = 32 / 2523.0
c1 = 3424 / 4096.0
c2 = 2413 / 128.0
c3 = 2392 / 128.0

def pq_to_lin(pq):
    p = pq ** m2inv
    d = max(p - c1, 0) / (c2 - c3 * p)
    return d ** m1inv

class patch:
    pN = 0 #patch number
    pR = 0 #patch red
    pG = 0 #patch green
    pB = 0 #patch blue
    pO = 0 #patch group order for shuffling

    pGR = 0 #patch gamma adjusted red
    pGG = 0 #patch gamma adjusted green
    pGB = 0 #patch gamma adjusted blue
    
    oW = 0 #WRGB OLED white drive approx
    oR = 0 #WRGB OLED red drive approx
    oG = 0 #WRGB OLED green drive approx
    oB = 0 #WRGB OLED blue drive approx
    oT = 0 #WRGB OLED total pixel drive approx

    def __init__(self, n,r,g,b):
        self.pN = n
        self.pR = r
        self.pG = g
        self.pB = b
        self.calc_gamma()
        self.calc_oled()

    def calc_oled(self):
        self.oR = self.pGR
        self.oG = self.pGG
        self.oB = self.pGB
        
        if prims != 2:
            self.oW = (min(self.pGR, self.pGG, self.pGB))
            
            if self.pGR>self.oW:
                self.oR=self.pGR-self.oW
            else:
                self.oR=0

            if self.pGG>self.oW:
                self.oG=self.pGG-self.oW
            else:
                self.oG=0
                
            if self.pGB>self.oW:
                self.oB=self.pGB-self.oW
            else:
                self.oB=0

        self.oT = self.oW + self.oR + self.oG + self.oB

    def calc_gamma(self):
        if dr == 2:
            self.pGR = pq_to_lin((self.pR - rangeStart)/(rangeEnd - rangeStart)) * 10000.
            self.pGG = pq_to_lin((self.pG - rangeStart)/(rangeEnd - rangeStart)) * 10000.
            self.pGB = pq_to_lin((self.pB - rangeStart)/(rangeEnd - rangeStart)) * 10000.
        else:
            self.pGR = ((self.pR - rangeStart)/(rangeEnd - rangeStart)) ** gamma * peaknits
            self.pGG = ((self.pG - rangeStart)/(rangeEnd - rangeStart)) ** gamma * peaknits
            self.pGB = ((self.pB - rangeStart)/(rangeEnd - rangeStart)) ** gamma * peaknits
        
    def print(self):
        print (self.pN, self.pO, self.pR, self.pG, self.pB, self.pGR, self.pGG, self.pGB, self.oW, self.oR, self.oG, self.oB, self.oT )

    def check_rolling(self, plist, aW,aR,aG,aB,aT):
        countW = 0
        countR = 0
        countG = 0
        countB = 0
        countT = 0
        for n in plist:
            countW = countW + n.oW
            countR = countR + n.oR
            countG = countG + n.oG
            countB = countB + n.oB
            countT = countT + n.oT
        avgW=( countW+self.oW ) /(len(plist)+1)
        avgR=( countR+self.oR ) /(len(plist)+1)
        avgG=( countG+self.oG ) /(len(plist)+1)
        avgB=( countB+self.oB ) /(len(plist)+1)
        avgT=( countT+self.oT ) /(len(plist)+1)
        diffW = abs(avgW-aW)
        diffR = abs(avgR-aR)
        diffG = abs(avgG-aG)
        diffB = abs(avgB-aB)
        diffT = abs(avgT-aT)
#       return (diffW + diffR  + diffG + diffB + diffT )        
        return (diffW **2 + diffR **2 + diffG **2 + diffB **2 + diffT **4)
#        return (diffT)

# check for enough arguments

print ("oledpatchsortSOFS8+")
print ("Enhancements by aron7awol based on original version:")
print ("oledpatchsortSOFS8 - (c) 2021 Auvien Limited")
print ("By James Finnie AKA jfinnie AKA bobof")
print ("Thanks to AVS @PencilGeek for some range mods")

global rangeStart
global rangeEnd

print ("Display Primaries:")
print ("1. WRGB (Default)")
print ("2. RGB")
prims = int (input())

print ("Dynamic Range:")
print ("1. SDR (Default)")
print ("2. HDR")
dr = int (input())

gamma = 2.2
peaknits = 100.0
if dr != 2:
    print ("Enter gamma:")
    gamma = float(input ())
    print ("Enter peak white (nits):")
    peaknits = float(input ())

if len(sys.argv)<2:
    print ("Invoking patch generator")
    print ("Patch set quantization:")
    print ("1. 8 bit (Default)")
    print ("2. 10 bit")
    print ("3. 12 bit")
    quantInput=int (input())
    if (quantInput == 2):
        quantBits=10
    elif (quantInput == 3):
        quantBits=12
    else:
        quantBits=8

    vidBlack=16*(2**(quantBits-8))
    fullBlack=0
    vidWhite=235*(2**(quantBits-8))
    extWhite=(2**quantBits)-1
    print ("Enter sample range:")
    print ("1. Full Range ("+str(fullBlack)+"-"+str(extWhite)+")")
    print ("2. Extended Range ("+str(vidBlack)+"-"+str(extWhite)+")(Default)")
    print ("3. Legal Range ("+str(vidBlack)+"-"+str(vidWhite)+")")
    sampleRange=int (input())
    if (sampleRange == 1):
        rangeStart = fullBlack
        rangeEnd = extWhite
        refBlack= fullBlack
    elif (sampleRange == 3):
        rangeStart = vidBlack
        rangeEnd = vidWhite
        refBlack = vidBlack
        refWhite = vidWhite
    else:
        rangeStart = vidBlack
        rangeEnd = extWhite
        refBlack = vidBlack

# If there's ever a need to allow the sample range to span [0, 255] but declare refBlack=16,
#  then uncomment out the following three lines.
#    if (rangeStart == 0):
#        print ("Enter reference black value: (eg 0, 16)")
#        refBlack=int(input ())

    if (rangeEnd == extWhite):
        print ("Enter reference white value: (eg "+str(vidWhite)+", "+str(extWhite)+" )")
        refWhite =int(input ())

    print ("Enter cube size: (eg 21 for 21^3 cube)")
    cubeSize=int(input ())
    print ("Enter number of enhanced intermediate RGBCMYW patches: (0,1,2,3,4)")
    extraPoints = int(input ())
    print ("Enter patch power: (1 for equdidstant, 1.1 for LS sequence)")
    patchPower = float(input ())
    inputfilename=str(cubeSize)+"p_"+str(extraPoints)+"extra_"+str(patchPower)+"power.csv"
    print ("Autogenerated nput filename:",inputfilename)
    #create patchset
    patchDivs = cubeSize - 1
    patchDiv = 1 / patchDivs

    patchVals = []
    patchlist = []

    for n in range(cubeSize):
        val = int (((rangeEnd-rangeStart) * (( n * patchDiv ) ** patchPower))) + rangeStart
        patchVals.append(val)

    print ("Old Cube Patch Values:" ,patchVals)
    
    # Insert reference black into patchset sequence by removing/replacing the closest value
    if refBlack not in patchVals:
        for n in range(len(patchVals) - 2):
            if (n == 0): continue
            if((patchVals[n] < refBlack) and (patchVals[n+1] > refBlack)):
                x1 = refBlack - patchVals[n]
                x2 = patchVals[n+1] - refBlack
                if (x1 <= x2):
                    patchVals[n] = refBlack
                else:
                    patchVals[n+1] = refBlack
        else:
            if refBlack not in patchVals:
                patchVals[1] = refBlack

    # Insert reference white into patchset sequence by removing/replacing the closest value
    if refWhite not in patchVals:
        for n in range(len(patchVals) - 2):
            if((patchVals[n] < refWhite) and (patchVals[n+1] > refWhite)):
                x1 = refWhite - patchVals[n]
                x2 = patchVals[n+1] - refWhite
                if (x1 <= x2):
                    patchVals[n] = refWhite
                else:
                    patchVals[n+1] = refWhite
        else:
            if refWhite not in patchVals:
                patchVals[len(patchVals)-2] = refWhite

    print ("New Cube Patch Values:" ,patchVals)

    count = 0

    for r in patchVals:
        for g in patchVals:
            for b in patchVals:
                patchlist.append(patch(count,r,g,b))
                count = count + 1

    if extraPoints > 0:
        extraDiv = 1 / (patchDivs * (extraPoints+1))
        extraVals = []
        for n in range((patchDivs*(extraPoints+1))+1):
            val = int (((rangeEnd-rangeStart) * (( n * extraDiv ) ** patchPower))) + rangeStart
            if val not in patchVals:
                extraVals.append(val)
        print ("Extra Patch Values:" ,extraVals)
        for e in extraVals:
                patchlist.append(patch(count,e,e,e))
                count = count + 1 
                patchlist.append(patch(count,e,refBlack,refBlack))
                count = count + 1        
                patchlist.append(patch(count,refBlack,e,refBlack))
                count = count + 1
                patchlist.append(patch(count,refBlack,refBlack,e))
                count = count + 1  
                patchlist.append(patch(count,e,e,refBlack))
                count = count + 1        
                patchlist.append(patch(count,refBlack,e,e))
                count = count + 1
                patchlist.append(patch(count,e,refBlack,e))
                count = count + 1
else:
    #open CSV input file and read into list
    patchlist=[]    
    inputfilename = sys.argv[1]
    print ("input patch file: ",inputfilename)
    with open (inputfilename,  encoding="utf-8-sig") as csv_file:
        minVal = 2**24 
        maxVal = 0
        reader = csv.reader(csv_file)
        for row in reader:
            minTmp = min(int(row[1]),int(row[2]),int(row[3]))
            maxTmp = max(int(row[1]),int(row[2]),int(row[3]))
            if minTmp < minVal:
                minVal = minTmp
            if maxTmp > maxVal:
                maxVal = maxTmp
        rangeStart = minVal
        rangeEnd = maxVal
        if rangeEnd <= 255:
            quantBits=8
        elif rangeEnd <= 1023:
            quantBits=10
        elif rangeEnd <= 4095:
            quantBits=12

    with open (inputfilename,  encoding="utf-8-sig") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            patchlist.append (patch(int(row[0]),int(row[1]),int(row[2]),int(row[3])))

patchRange = str(rangeStart)+"-"+str(rangeEnd) 
print ("Patch range: "+patchRange)
print ("Patch set quantization: "+str(quantBits)+"b")
verstring = verstring + "_" + str(quantBits) + "b_"+patchRange
outputfilename = verstring +"_"+ inputfilename
print ("output patch file: ",outputfilename)

print ("Enter preroll sequence size: ")
preRoll = int(input ())
if preRoll > 0:
    print ("Enter preroll drift patch interval: ")
    driftInt = int(input ())
    print ("Enter preroll drift patch value: ")
    driftVal = int(input ())    
    driftfilename=verstring+"_"+str(preRoll)+"preroll_"+str(driftInt)+"drift_"+str(driftVal)+"driftval_"+inputfilename

    print ("Drift filename:",driftfilename)

#remove white and black patches.  We'll add them back later in the required places for LS
#but for now, they just get in the way
#also calculate set averages


patchlistSize = len(patchlist)

avgW = 0
avgR = 0
avgG = 0
avgB = 0
avgT = 0

for patchInst in patchlist:
    if patchInst.pR == rangeEnd and patchInst.pG == rangeEnd and patchInst.pB == rangeEnd:
        print ("found white patch, removing")
        patchlist.remove (patchInst)
for patchInst in patchlist:
    if patchInst.pR == rangeStart and patchInst.pG == rangeStart and patchInst.pB == rangeStart:
        print ("found black patch, removing")
        patchlist.remove (patchInst)

for patchInst in patchlist:
    avgW = avgW + patchInst.oW
    avgR = avgR + patchInst.oR
    avgG = avgG + patchInst.oG
    avgB = avgB + patchInst.oB
    avgT = avgT + patchInst.oT
# print ("patchlist size: ",len(patchlist))

avgW = avgW / patchlistSize
avgR = avgR / patchlistSize
avgG = avgG / patchlistSize
avgB = avgB / patchlistSize
avgT = avgT / patchlistSize
print ("AVG WRGBT",avgW,avgR,avgG,avgB,avgT)

count = 1
check = 200
sumtot = 0
sumnum = 15
prevtot = -1

print ("Initial shuffle to make sure every value is shuffled at least twice")
for loop in range(2):
    for shufflepatch in patchlist:
    #    for shufflepatch in patchlist[worstpos-sumnum:worstpos]+patchlist[len(patchlist)-1:len(patchlist)]:
            savepatch=shufflepatch
            patchlist.remove (shufflepatch)
            bestPos = -1
            bestAvg = -1
#            for findhole in range (sumnum,len(patchlist)):
            for findhole in range (sumnum,len(patchlist),sumnum):
                curAvg = savepatch.check_rolling (patchlist [findhole-sumnum:findhole],avgW, avgR, avgG, avgB, avgT)
                if bestPos == -1:
                    bestPos = findhole
                    bestAvg = curAvg
                else:
                    if curAvg < bestAvg:
                        bestPos = findhole
                        bestAvg = curAvg
            patchlist.insert (int(bestPos-(sumnum/2)),savepatch)

        
print ("Iterating over patchset until further improvement not likely")
for loop in range(int((1000*patchlistSize)/sumnum)):
    # print (loop)
    sumT = []
    sumW = []
    sumR = []
    sumG = []
    sumB = []
    xaxis = []
    worstpos = 0
    worstdiff = 0
    for n in range (sumnum,len(patchlist),sumnum):
        tempT = 0
        tempW = 0
        tempR = 0
        tempG = 0
        tempB = 0
        for o in patchlist [n-sumnum:n]:
            tempT = tempT + o.oT
            tempW = tempW + o.oW
            tempR = tempR + o.oR
            tempG = tempG + o.oG
            tempB = tempB + o.oB
        sumT.append (tempT)
        sumW.append (tempW)
        sumR.append (tempR)
        sumG.append (tempG)
        sumB.append (tempB)
        xaxis.append (n)

        currdiff = abs ((avgT*sumnum)-tempT) + abs ((avgW*sumnum)-tempW) + abs ((avgR*sumnum)-tempR) + abs ((avgG*sumnum)-tempG) + abs ((avgB*sumnum)-tempB)
#       currdiff = abs ((avgT*sumnum)-tempT) **4 + abs ((avgW*sumnum)-tempW) **2 + abs ((avgR*sumnum)-tempR) **2 + abs ((avgG*sumnum)-tempG) **2 + abs ((avgB*sumnum)-tempB)**2 
#       currdiff = abs ((avgT*sumnum)-tempT)
        
        if currdiff > worstdiff:
            worstdiff = currdiff
            worstpos = n
    if count == check:
        if prevtot == -1:
            prevtot = sumtot
            print ("Check progress... pass "+str(loop+1)+": Current total "+str(sumtot))
        else:
            print ("Check progress... pass "+str(loop+1)+": Is current total "+str(sumtot)+" less than previous total "+str(prevtot)+"?")
            if prevtot > sumtot:
                prevtot = sumtot
            else:
                print ("No it isn't - break!")
                break
        count = 1
        sumtot = 0    
    else:
        count = count + 1
        sumtot = sumtot + worstdiff
    
    #print (worstpos, worstdiff)
    #shuffle the worst patch group and the first and last patch in the set
    for shufflepatch in patchlist[worstpos-sumnum:worstpos]+patchlist[len(patchlist)-1:len(patchlist)]+patchlist[0:1]:
#    for shufflepatch in patchlist[worstpos-sumnum:worstpos]:
        savepatch=shufflepatch
        patchlist.remove (shufflepatch)
        bestPos = -1
        bestAvg = -1
        for findhole in range (sumnum,len(patchlist),sumnum):
#        for findhole in range (sumnum,len(patchlist)):
            curAvg = savepatch.check_rolling (patchlist [findhole-sumnum:findhole],avgW, avgR, avgG, avgB, avgT)
            if bestPos == -1:
                bestPos = findhole
                bestAvg = curAvg
            else:
                if curAvg < bestAvg:
                    bestPos = findhole
                    bestAvg = curAvg
        patchlist.insert (int(bestPos-(sumnum/2)),savepatch)

print ("Adding black and white patches back in correct positions")
patchlist.insert (0, patch(0,rangeStart,rangeStart,rangeStart))   
patchlist.append (patch(len(patchlist),rangeEnd,rangeEnd,rangeEnd))

print ("output patchlist size: ",len(patchlist))

#write out to CSV
with open(outputfilename, mode='w',newline="\n", encoding="utf-8") as out_file:
    writer = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)
    for n in range (0,len(patchlist)):
        writer.writerow([n,patchlist[n].pR, patchlist[n].pG, patchlist[n].pB ])

with open("debug_"+outputfilename, mode='w',newline="\n", encoding="utf-8") as out_file:
    writer = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)
    for n in range (0,len(patchlist)):
        writer.writerow([n,patchlist[n].pR, patchlist[n].pG, patchlist[n].pB, patchlist[n].pGR, patchlist[n].pGG, patchlist[n].pGB, patchlist[n].oW, patchlist[n].oR, patchlist[n].oG, patchlist[n].oB, patchlist[n].oT])

# sort out a preroll set with drift patches etc.

if preRoll > 0:
    if preRoll > (len (patchlist) -2):
        preRoll = len (patchlist) -2
    driftlist = patchlist [1:preRoll+1]
    driftlist.reverse()
    for i in range (int (preRoll / driftInt)):
        driftlist.insert(((i*driftInt)+i), patch (0,driftVal,driftVal,driftVal))
    with open(driftfilename, mode='w',newline="\n", encoding="utf-8") as out_file:
        writer = csv.writer(out_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONE)
        for n in range (0,len(driftlist)):
            writer.writerow([n,driftlist[n].pR, driftlist[n].pG, driftlist[n].pB])
       
sys.exit()
