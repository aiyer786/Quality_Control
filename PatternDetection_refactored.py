class PatternDetection:
    class PlaceHolderNode:
        def __init__(self):
            self.LP = -float("inf")
            self.SP = -float("inf")
        
    def CheckPattern(self,lptr, rptr, period, bin_data,min_rep):
        """
        Function used to check whether there exist a pattern of appropriate length within the given interval

        Arguments:
        lptr -- the starting index for the search
        rptr -- the ending index for the search
        period -- the length of the pattern to search for
        bin_data -- the data to search within

        Return:
        valid -- a boolean indicating if a pattern was found
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
                        break
        return valid


    def PeriodicityCheck(self,bin_data, period, min_rep):
        """
        Perform periodicity check and validation on the binary data for a given period

        Arguments:
        bin_data -- the data to search within
        period -- the length of the pattern to search for
        min_rep -- the minimum number of repetitions of the pattern required to declare a match

        Return:
        valid -- a boolean indicating if a pattern was found
        """
        # Create a list of PlaceholderNodes for each position in the period
        PlaceHolder = [self.PlaceHolderNode() for _ in range(period)]
        # Initialize the LP (last position) and SP (start position) of each PlaceholderNode
        for i in range(period):
            PlaceHolder[i].LP = i % period
            PlaceHolder[i].SP = i % period
        valid = False
        pos = (len(bin_data) - 1 ) % period
        # Iterate through the binary data starting from the end of the period
        for i in range(period, len(bin_data)):
            pos = i % period
            # If the current element matches with the LP of the corresponding placeholder node, update the LP
            if (bin_data[PlaceHolder[pos].LP] == bin_data[i]):
                PlaceHolder[pos].LP = i
                continue
            else:
                # If there is a pattern in the range between SP and LP, consider it as a valid pattern
                if self.CheckPattern(PlaceHolder[pos].SP, PlaceHolder[pos].LP, period, bin_data,min_rep):
                    valid = True
                    break
                    # continue
                
                # Otherwise, update the SP and LP for the corresponding placeholder node
                PlaceHolder[pos].SP = i
                PlaceHolder[pos].LP = i
        # Check if a pattern is found between the start and last positions for the last position in the period
        if self.CheckPattern(PlaceHolder[pos].SP, PlaceHolder[pos].LP, period, bin_data,min_rep):
            valid = True
        return valid


    def PTV(self,tags, Lmin, Lmax, min_rep):
        """
        Searches for a repeating pattern in the given binary data within the period range [Lmin, Lmax].
        Prints a message if a pattern is found, or "Pattern not found" otherwise.

        Arguments:
        bin_data -- the data to search within
        Lmin -- the minimum length of the pattern to search for
        Lmax -- the maximum length of the pattern to search for
        min_rep -- the minimum number of repetitions of the pattern required to declare a match
        """
        tags.sort(key = lambda l: l.created_at)
        bin_data = []
        for i in tags:
            bin_data.append(i.value)
        # Initialize a boolean flag to keep track of whether a pattern has been found
        pattern_found = False

        # Iterate over all possible period lengths from Lmin to Lmax
        for period in range(Lmin, Lmax + 1):
            # Check for periodicity using the PeriodicityCheck function
            if (self.PeriodicityCheck(bin_data, period, min_rep)):
                # If a pattern is found, set the flag to True and exit the loop
                pattern_found = True
                break

        if not pattern_found:
            return("Pattern not found")
            # print("Pattern not found")
        else:
            return ("Pattern found")
            # print("Pattern found")


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
# bin_data = [1, 1, 0, 1, 1, 1, 0, 1, 0, 1]

# bin_data = [0,0,0,1,1,1,0,0,1,1,0,0]  # No Pattern
# bin_data = [1, 0, 1, 1, 0, 0, 1, 0, 0, 0]  # No Pattern

# Lmin = 2  # Minimum period length
# Lmax = 6  # Maximum period length
# min_rep = 2  # Minimum number of repetitions for a periodic pattern
# x = PatternDetection()
# x.PTV(bin_data, Lmin, Lmax, min_rep)