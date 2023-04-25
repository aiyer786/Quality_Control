class PatternDetection:
    # Main Class for Pattern Recognition
    class PlaceHolderNode:
        # Sub class used for custom data structure
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
        Result -- a list containing a boolean for pattern found, pattern,and repitition
        """
        result = 3*[False]
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
                result[0] = pattern_list[0]
                result[1] = len(pattern_list)
                result[2] = True
        return result


    def PeriodicityCheck(self,bin_data, period, min_rep):
        """
        Perform periodicity check and validation on the binary data for a given period

        Arguments:
        bin_data -- the data to search within
        period -- the length of the pattern to search for
        min_rep -- the minimum number of repetitions of the pattern required to declare a match

        Return:
        Result -- a list containing a boolean for pattern found, pattern,and repitition
        """
        result = 3*[False]
        # Create a list of PlaceholderNodes for each position in the period
        PlaceHolder = [self.PlaceHolderNode() for _ in range(period)]
        # Initialize the LP (last position) and SP (start position) of each PlaceholderNode
        for i in range(period):
            PlaceHolder[i].LP = i % period
            PlaceHolder[i].SP = i % period
        valid = False
        pos = (len(bin_data) - 1 ) % period
        # Iterate through the data starting from the end of the period
        for i in range(period, len(bin_data)):
            pos = i % period
            # If the current element matches with the LP of the corresponding placeholder node, update the LP
            if (bin_data[PlaceHolder[pos].LP] == bin_data[i]):
                PlaceHolder[pos].LP = i
                continue
            else:
                # If there is a pattern in the range between SP and LP, consider it as a valid pattern
                result = self.CheckPattern(PlaceHolder[pos].SP, PlaceHolder[pos].LP, period, bin_data,min_rep)
                if result[2]:
                    return result
                    # continue
                
                # Otherwise, update the SP and LP for the corresponding placeholder node
                PlaceHolder[pos].SP = i
                PlaceHolder[pos].LP = i
        # Check if a pattern is found between the start and last positions for the last position in the period
        result = self.CheckPattern(PlaceHolder[pos].SP, PlaceHolder[pos].LP, period, bin_data,min_rep)
        if result[2]:
            return result
        return result


    def PTV(self,tags, Lmin, Lmax, min_rep):
        """
        Searches for a repeating pattern in the given binary data within the period range [Lmin, Lmax].
        Updates the result list whether pattern is found or not and then return the result list

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
        # Initialize a boolean flag and result list to keep track of whether a pattern has been found
        result = []
        pattern_found = False

        # Iterate over all possible period lengths from Lmin to Lmax
        for period in range(Lmin, Lmax + 1):
            # Check for periodicity using the PeriodicityCheck function
            result = self.PeriodicityCheck(bin_data, period, min_rep)
            if (result[2]):
                # If a pattern is found, set the flag to True and exit the loop
                pattern_found = True
                result[2] = "Pattern_Found"
                break

        if not pattern_found:
            result[2] = "Pattern_not_found"
            return result
            
        else:
            return result
            