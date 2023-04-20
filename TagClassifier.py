import numpy as np
from collections import Counter


class TagClassifier:
    def calculateAgreementDisagreement(self, data) -> dict:
        """
        Calculates Agreement/Disagreement of the users with other users per their tags 

        Args:
            data (array): 2d array where columns represent raters and rows represents tag_promot_ids

        Returns:
            dict: dictionary of tags representing fractions of major .....
        """
        num_tags = data.shape[0]
        raters = data.shape[1]
        tags = {}
        for i in range(num_tags):
            row = []
            answer_id = None
            tag_prompt_id = None
            for j in range(raters):
                if data[i,j] is not None:
                    #print(data[i,j])
                    row.append(data[i,j].value)
                    if not answer_id:
                        answer_id = data[i,j].answer_id 
                    if not tag_prompt_id:
                        tag_prompt_id = data[i,j].tag_prompt_id
            counter = Counter(row)
            val,freq = counter.most_common(1)[0]
            result = freq/raters
            tags[answer_id] = {tag_prompt_id: [val, result]}
        return tags
