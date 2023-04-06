import math
import numpy as np
import krippendorff
from scipy import stats as st

class TaggerClassifier:
    """
    Class containing methods to tag a classifier as reliable/unreliable
    """
    def intervalLogs(self, tags) -> int:
        """
        Gets the time difference in seconds between subsequent tags, applies log base 2 to the result, 
        and finally averages the result to return it
        Args:
            tags (list): list of answer tags

        Returns:
            int: interval logs value for a tagger
        """
        if len(tags)==1:
            return -1                                       # Need to be discussed
        
        tags.sort(key = lambda l: l.created_at)             # sorting the tags based on created_at
        result = 0
        
        curr = 0
        # Adding the log of time difference in seconds
        for ind in range(1, len(tags)):
            curr += (tags[ind].created_at - tags[ind-1].created_at).total_seconds()
        
        result = math.log(curr,2) if curr>0 else 0              # if time difference is 0 then add 0
        # Taking average
        result = result/(len(tags)-1)
        return result
    
    def getKrippendorffAlpha(self, data):
        #data = data.T
        # Replace 4 with the number of rating categories in your data
        num_raters = data.shape[1]
        alphas = []
        for i in range(num_raters):
            rater_data = data[:, i]
            #print("Observed Data = ",set(rater_data))
            other_data = np.delete(data, i, axis=1)
            #print(other_data)
            #expected_data = np.mean(other_data, axis=1)
            expected_data = []
            for edata in other_data:
                expected_data.append(st.mode(edata).mode[0])
            #print("Expected data = ", set(expected_data))
            expected_data = np.array(expected_data)
            #expected_data = st.mode(other_data.T).mode[0]
            if(len(set(expected_data))==1) or (len(set(expected_data))==2 and 'nan' in set(expected_data)):
                alphas.append(np.nan)
                continue
            alpha = krippendorff.alpha(np.array([rater_data, expected_data]), level_of_measurement='nominal')
            alphas.append(alpha)
        return alphas
        
    
    
    