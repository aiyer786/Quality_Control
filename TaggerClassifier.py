import math
import numpy as np
import krippendorff
from scipy import stats as st

class TaggerClassifier:
    """
    Class containing methods to tag a classifier as reliable/unreliable
    """
    def buildIntervalLogs(self, tags) -> int:
        """
        Gets the time difference in seconds between subsequent tags, applies log base 2 to the result, 
        and finally return the average
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
            try:
                curr += math.log((tags[ind].created_at - tags[ind-1].created_at).total_seconds(),2)
            except:
                curr+=0
        
        # Taking average
        result = curr/(len(tags)-1)
        return result
    
    def computeKrippendorffAlpha(self, data, users) -> list:  #getKrippendorffAlpha
        """
        Krippendorff alpha algorithm implementation using krippendorff library

        Args:
            data (array): 2d array where columns represent raters and rows represents tag_promot_ids

        Returns:
            list: list of alpha values of all users
        """
        #data = data.T
        num_raters = len(users)
        alphas = {}
        for i in range(num_raters):
            rater_data = data[:, i]
            other_data = np.delete(data, i, axis=1)
            expected_data = []
            for tags in other_data:
                # Calculating mode of all the other raters data
                expected_data.append(st.mode(tags).mode[0])
            
            expected_data = np.array(expected_data)
            if(len(set(expected_data))==1) or (len(set(expected_data))==2 and 'nan' in set(expected_data)):
                alphas[users[i]] = np.nan
                continue
            
            alpha = krippendorff.alpha(np.array([rater_data, expected_data]), level_of_measurement='nominal')
            alphas[users[i]] = alpha
        return alphas
        
    
    
    