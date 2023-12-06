class PatternDetection:
    # Main Class for Pattern Recognition
    class PlaceHolderNode:
        # Sub class used for custom data structure
        def __init__(self):
            self.LP = -float("inf")
            self.SP = -float("inf")
        
    def CheckPattern(self,lptr, rptr, period, bin_data,min_tags):
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
        if (len(pattern_list)>1 and len(pattern_list)*len(pattern_list[0]) >= min_tags):
            if len(set(pattern_list)) == 1:
                result[0] = pattern_list[0]
                result[1] = len(pattern_list)
                result[2] = True
        return result


    def PeriodicityCheck(self,bin_data, period, min_tags):
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
                result = self.CheckPattern(PlaceHolder[pos].SP, PlaceHolder[pos].LP, period, bin_data,min_tags)
                if result[2]:
                    return result
                    # continue
                
                # Otherwise, update the SP and LP for the corresponding placeholder node
                PlaceHolder[pos].SP = i
                PlaceHolder[pos].LP = i
        # Check if a pattern is found between the start and last positions for the last position in the period
        result = self.CheckPattern(PlaceHolder[pos].SP, PlaceHolder[pos].LP, period, bin_data,min_tags)
        if result[2]:
            return result
        return result


    def PTV(self, tags, Lmin, Lmax, min_tags):
        tags.sort(key=lambda l: l.created_at)
        bin_data = [i.value for i in tags]

        patterns_found = []
        for period in range(Lmin, Lmax + 1):
            pattern_results = self.PeriodicityCheckAllPatterns(bin_data, period, min_tags)
            for pattern, count in pattern_results:
                if not any(set(pattern).issubset(set(p[0])) for p in patterns_found):
                    patterns_found.append((pattern, count))

        if not patterns_found:
            return [("Not_found", 0)]
        else:
            return patterns_found

    def PeriodicityCheckAllPatterns(self, bin_data, period, min_tags):
        PlaceHolder = [self.PlaceHolderNode() for _ in range(period)]
        for i in range(period):
            PlaceHolder[i].LP = i % period
            PlaceHolder[i].SP = i % period

        patterns = []
        for i in range(period, len(bin_data)):
            pos = i % period
            if bin_data[PlaceHolder[pos].LP] == bin_data[i]:
                PlaceHolder[pos].LP = i
                continue
            else:
                result = self.CheckPattern(PlaceHolder[pos].SP, PlaceHolder[pos].LP, period, bin_data, min_tags)
                if result[2]:
                    if result[0] not in (p[0] for p in patterns):
                        patterns.append((result[0], result[1]))
                
                PlaceHolder[pos].SP = i
                PlaceHolder[pos].LP = i

        pos = (len(bin_data) - 1) % period
        result = self.CheckPattern(PlaceHolder[pos].SP, PlaceHolder[pos].LP, period, bin_data, min_tags)
        if result[2]:
            if result[0] not in (p[0] for p in patterns):
                patterns.append((result[0], result[1]))

        return patterns