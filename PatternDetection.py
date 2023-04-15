# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 13:16:32 2023

@author: Darshan
"""
class PlaceHolderNode:
    def __init__(self):
        self.LP = -float("inf")
        self.SP = -float("inf")

def CheckPattern(lptr, rptr, period, bin_data):
    valid = False
    pattern_list = []
    # for i in range(PlaceHolder[0].SP, PlaceHolder[-1].SP + 1, period):
    for i in range(lptr, rptr + 1, period):
        pattern = bin_data[i: i + period]
        if len(pattern ) == period:
            pattern_list.append(tuple(pattern ))
            # print(pattern)
            if (len(pattern_list) >= min_rep):
                if len(set(pattern_list)) == 1:
                    print("Pattern found:", pattern_list[0], "\nRepetitions:", len(pattern_list), "\nStarting Position:", lptr)
                    valid = True
    return valid

def PeriodicityCheck(bin_data, period, min_rep):
    # print("PERIOD: ", period)
    PlaceHolder = [PlaceHolderNode() for _ in range(period)]
    # Initialization
    for i in range(period):
        PlaceHolder[i].LP = i % period
        PlaceHolder[i].SP = i % period
        # print(PlaceHolder[i].SP, PlaceHolder[i].LP)
    # Validation
    valid = False
    for i in range(period, len(bin_data)):
        pos = i % period
        if (bin_data[PlaceHolder[pos].LP] == bin_data[i]):
            PlaceHolder[pos].LP = i
            # print(pos, PlaceHolder[pos].SP, PlaceHolder[pos].LP)
            continue
        else:
             if CheckPattern(PlaceHolder[pos].SP, PlaceHolder[pos].LP, period, bin_data):
                 valid = True
                 continue
             PlaceHolder[pos].SP = i
             PlaceHolder[pos].LP = i
        # print(pos, PlaceHolder[pos].SP, PlaceHolder[pos].LP)
    # Rechecking        
    if CheckPattern(PlaceHolder[pos].SP, PlaceHolder[pos].LP, period, bin_data):
        valid = True
    return valid


def PTV(bin_data, Lmin, Lmax, min_rep):
    # Phase I
    pattern_found = False
    for period in range(Lmin, Lmax + 1):
        if (PeriodicityCheck(bin_data, period, min_rep)):
            pattern_found = True
    if not pattern_found:
        print("Pattern not found")


# bin_data = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0] 
# bin_data = [0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0]
# bin_data = [0,0,0,1,1,0,0,1,1,1,0,0,1,1,0,0,1,1,0,0,0]
# bin_data = [1,0,0,0,1,1,1,0,0,0,1,1,0,1,0,0,0]
# bin_data = [1,0,1,1,1,0,0,1,1,0,0,1,1,0,0,1] 
# bin_data = [1,0,1,1,1,0,0,1,1,0,0,1,1,0,0,1] 
# bin_data = [0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0]
# bin_data = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
# bin_data = [0, 1, 0, 0, 1, 0, 0, 1, 0, 1]
# bin_data = [1, 1, 0, 1, 1, 0, 1, 1, 0, 1]
bin_data = [1, 1, 0, 1, 1, 1, 0, 1, 0, 1]

# bin_data = [0,0,0,1,1,1,0,0,1,1,0,0]  # No Pattern
# bin_data = [1, 0, 1, 1, 0, 0, 1, 0, 0, 0]  # No Pattern

Lmin = 2  # Minimum period length
Lmax = 6  # Maximum period length
min_rep = 2  # Minimum number of repetitions for a periodic pattern
PTV(bin_data, Lmin, Lmax, min_rep)