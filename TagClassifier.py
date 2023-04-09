import numpy as np
from scipy import stats as st


class TagClassifier:
    def calculateAgreementDisagreement(self, data) -> dict:
        """
        Calculates Agreement/Disagreement of the users with other users per their tags 

        Args:
            data (array): 2d array where columns represent raters and rows represents tag_promot_ids

        Returns:
            dict: dictionary of users to the agreement/disagreement of each of their tags
        """
        num_raters = data.shape[1]
        users = {}
        for i in range(num_raters):
            tags = []
            rater_data = data[:, i]
            other_data = np.delete(data, i, axis=1)
            expected_data = []
            for edata in other_data:
                expected_data.append(st.mode(edata).mode[0])
            
            for i in range(len(expected_data)):
                if rater_data[i]==np.nan or expected_data[i]==np.nan:
                    tags.append(0)
                elif rater_data[i]==expected_data[i]:
                    tags.append(1)
                else:
                    tags.append(-1)
                    
            users[i] = tags
        return users
