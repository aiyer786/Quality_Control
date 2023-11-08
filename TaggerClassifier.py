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
    
    def computeKrippendorffAlpha(self, data, users) -> list:
        """
        Krippendorff alpha algorithm implementation using krippendorff library
        
        Args:
            data (array): 2d array where columns represent raters and rows represents tag_promot_ids
        
        Returns:
            list: list of alpha values of all users
        """
        num_raters = len(users)
        alphas = {}
        for i in range(num_raters):
            rater_data = data[:, i].astype(np.float64)  # Convert to float to ensure numeric types
            other_data = np.delete(data, i, axis=1).astype(np.float64)
            expected_data = []
            for tags in other_data:
                numeric_tags = tags[~np.isnan(tags)]
                if numeric_tags.size > 0:
                    mode_result = st.mode(numeric_tags)
                    mode_value = mode_result.mode if mode_result.mode.size > 0 else np.nan
                    expected_data.append(mode_value)
                else:
                    expected_data.append(np.nan)
                
            expected_data = np.array(expected_data)
            
            # Skip calculation if there's not enough variation
            if np.nanstd(expected_data) == 0:
                alphas[users[i]] = np.nan
                continue
            
            try:
                alpha = krippendorff.alpha(np.array([rater_data, expected_data]), level_of_measurement='nominal')
                alphas[users[i]] = alpha
            except ValueError:
                # Handle the case where there's not enough variation to compute alpha
                alphas[users[i]] = 'not enough variation'
                
        return alphas