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
        and finally return the average, as well as the number of tags
        Args:
            tags (list): list of answer tags

        Returns:
            int: interval logs value for a tagger
        """
        if len(tags)==1:
            return (-1,1)                                       # Need to be discussed
        
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
        return (result, len(tags))
    

    def intervalLogsForTags(self, tags):
        """
        Calculates the interval log value for each tag.

        Args:
            tags (list): List of tags, each with a created_at attribute.

        Returns:
            dict: Dictionary with tag IDs as keys and interval log values as values.
        """
        interval_logs = {}
        sorted_tags = sorted(tags, key=lambda tag: tag.created_at)

        for i in range(1, len(sorted_tags)):
            current_tag = sorted_tags[i]
            previous_tag = sorted_tags[i-1]
            time_diff = (current_tag.created_at - previous_tag.created_at).total_seconds()

            # Avoid negative or zero time differences
            if time_diff <= 0:
                continue

            # Calculate the interval log value
            il_value = math.log(time_diff, 2)
            interval_logs[current_tag.id] = il_value

        return interval_logs


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
    
    def calculate_tag_credibility_score(self, user_history):
        """
        Calculates the credibility score for each tag in user_history based on fast tagging log values and Krippendorff's alpha.

        Args:
            user_history (list): List of tag history items, each with attributes such as created_at, user_id, and tag values.

        Returns:
            dict: A dictionary with tag IDs as keys and credibility scores as values.
        """
        # Extract tags and users from user_history
        tags = user_history
        users = list(set(tag.user_id for tag in user_history))

        # Prepare data for Krippendorff's alpha calculation
        # Assuming that each row in data represents a tag and each column represents a user's rating for that tag
        tag_ids = [tag.id for tag in user_history]
        data = np.full((len(tag_ids), len(users)), np.nan)
        for i, tag in enumerate(user_history):
            user_index = users.index(tag.user_id)
            data[i, user_index] = tag.value  # Assuming 'value' is the rating given by the user for the tag

        credibility_scores = {}

        # Calculate interval logs for each tag
        interval_logs = self.intervalLogsForTags(tags)

        # Calculate Krippendorff's alpha for each tag
        alphas = self.computeKrippendorffAlpha(data, users)


        # Normalize values (assuming il_value and alpha_value are already in a suitable range)
        max_il_value = max(interval_logs.values(), default=1)
        max_alpha_value = 1  # Assuming alpha values are between 0 and 1

        # Calculate credibility score for each tag
        for tag in tags:
            tag_id = tag.id
            il_value = interval_logs[tag_id] if tag_id in interval_logs else 0
            alpha_value = alphas[tag_id] if tag_id in alphas else 0

            normalized_il = il_value / max_il_value if max_il_value > 0 else 0
            normalized_alpha = (alpha_value+1) / 2 if max_alpha_value > 0 else 0

            # Calculate credibility score
            credibility_score = (normalized_il + normalized_alpha) / 2
            credibility_scores[tag_id] = credibility_score

        return credibility_scores
