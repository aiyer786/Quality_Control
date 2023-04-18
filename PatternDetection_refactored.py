class PlaceHolderNode:
    def __init__(self):
        self.LP = -float("inf")
        self.SP = -float("inf")
    
def CheckPattern(lptr, rptr, period, bin_data):
    """
    Function used to check whether there exist a pattern of appropriate length within the given interval
    """
    valid = False
    pattern_list = []

    # Loop through the range of positions for the given period and check for patterns
    for i in range(lptr, rptr + 1, period):
        pattern = bin_data[i: i + period]

        # If pattern is of the given period length, add it to the pattern_list
        if len(pattern ) == period:
            pattern_list.append(tuple(pattern ))

            # If the pattern has occurred minimum number of times, and all the occurrences are same, print the pattern
            if (len(pattern_list) >= min_rep):
                if len(set(pattern_list)) == 1:
                    print("Pattern found:", pattern_list[0], "\nRepetitions:", len(pattern_list), "\nStarting Position:", lptr)
                    valid = True
    return valid


def PeriodicityCheck(bin_data, period, min_rep):
    """
    Perform periodicity check and validation on the binary data for a given period
    """
    PlaceHolder = [PlaceHolderNode() for _ in range(period)]
    # Initialization
    for i in range(period):
        PlaceHolder[i].LP = i % period
        PlaceHolder[i].SP = i % period
    # Validation
    valid = False
    for i in range(period, len(bin_data)):
        pos = i % period
        # If the current element matches with the LP of the corresponding placeholder node, update the LP
        if (bin_data[PlaceHolder[pos].LP] == bin_data[i]):
            PlaceHolder[pos].LP = i
            continue
        else:
            # If there is a pattern in the range between SP and LP, consider it as a valid pattern
             if CheckPattern(PlaceHolder[pos].SP, PlaceHolder[pos].LP, period, bin_data):
                 valid = True
                 continue
             
             # Otherwise, update the SP and LP for the corresponding placeholder node
             PlaceHolder[pos].SP = i
             PlaceHolder[pos].LP = i
    # Rechecking        
    if CheckPattern(PlaceHolder[pos].SP, PlaceHolder[pos].LP, period, bin_data):
        valid = True
    return valid


def PTV(bin_data, Lmin, Lmax, min_rep):
    """
    Given the Minimum period length(Lmin), Maximum Period Length(Lmax), minimum repetition count(min_rep), the function checks whether exists any pattern in the given data
    """
    pattern_found = False

    # Loop through the range of pattern lengths and perform periodicity check and validation
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