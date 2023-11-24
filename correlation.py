import pandas as pd
import os
from MySQL import MySQL
from collections import defaultdict
import numpy as np


class Correlation:

    def __init__(self) -> None:
        #self._connector = MySQL()                       # MySQL connector to call methods of MySQL class
        self.assignment_to_user = defaultdict(dict)
        #self.getUserTags()

        self.manual_grades = pd.read_excel("Manual_grades.xlsx")
        
        self.interval_logs_result = pd.read_csv("Interval_logs.csv")

        self.krippendorf_alpha_result = pd.read_csv("krippendorff.csv")

        self.agreement_disagreement_result = pd.read_csv("tags.csv")

        self.pattern_detection_result = pd.read_csv("Pattern_recognition.txt", sep='/')

    def __getUserTags(self):
        tags = self._connector.getAnswerTags()
        self.records = pd.DataFrame(columns=["Assignment_id", "User_id", "Answer_id", "Tag_prompt_id", "Value"])
        count = 0
        for tag in tags:
            data = {"Assignment_id": tag.assignment_id, "User_id": tag.user_id, "Answer_id": tag.answer_id, "Tag_prompt_id": tag.tag_prompt_id, "Value":tag.value}
            data = pd.DataFrame(data, index=[count])
            self.records = pd.concat([self.records, data])
            print(count)
            count+=1

        f=open("trial.csv", "w")
        f.write("Assignment_id,User_id,Answer_id,Tag_prompt_id,Value\n")
        for index, row in self.records.iterrows():
            f.write(str(row["Assignment_id"])+ "," + str(row["User_id"])+ "," + str(row["Answer_id"])+ "," + str(row["Tag_prompt_id"])+ "," + str(row["Value"])+ "\n")
        f.close()


    def sortManualGrades(self):
        self.manual_grades = self.manual_grades.sort_values('Assignment Id', ascending=False)

    def modifyIntervalLogsResults(self):
        self.interval_logs_result["IL_result"] = self.interval_logs_result["IL_result"].apply(lambda x: 1 if float(x)>=1.0 else -1)
        print(self.interval_logs_result)
    
    def __generateAgreementDisagreemtScore(self, observed_value, computed_value, fraction):
        #fraction = fraction.trim()
        #print(observed_value, computed_value, fraction)
        if float(fraction) < 0.5:
            return float(fraction)
        else:
            if float(computed_value) == float(observed_value):
                return float(fraction)
            else:
                return 1 - float(fraction)

    def convertToInt(self, x):
        if (x):
            return np.nan
        else:
            return int(x)

    def computeFinalScore(self, x):
        il_result = x[2]
        agreement_disagreement = x[3]
        krippenddorff_alpha = x[5]
        pattern = x[8]
        #print(pattern)

        if il_result=='nan':
            il_result=-1
        if agreement_disagreement=='nan':
            agreement_disagreement=-1
        if krippenddorff_alpha=='nan':
            krippenddorff_alpha=-1
        if pattern=='nan':
            pattern=-1
        res =  float(il_result) + float(agreement_disagreement) + float(krippenddorff_alpha) + float(pattern)
        return ((res+4)/8)*10

    def convertToQuadrant(self, x):
        if x<2:
            return 1
        elif 2<=x<4:
            return 3
        elif 4<=x<6:
            return 5
        elif 6<=x<8:
            return 7
        else:
            return 9

    def modifyAgreementDisagreemt(self):
        #self.__getUserTags()
        #print("User tags recorded..........")
        self.modifyIntervalLogsResults()
        self.records = pd.read_csv("trial.csv")
        self.records = pd.merge(self.records, self.agreement_disagreement_result, on=['Assignment_id', 'Answer_id', 'Tag_prompt_id'])
        self.interval_logs_result['User_id'] = self.interval_logs_result['User_id'].astype(pd.Int64Dtype())

        self.interval_logs_result["Agreement_Disagreement_Score"] = self.records.apply(lambda x: self.__generateAgreementDisagreemtScore(x[4], x[6], x[7]), axis=1)

        self.interval_logs_result = pd.merge(self.interval_logs_result, self.krippendorf_alpha_result, on=['Assignment_id', 'User_id'], how='left')

        self.interval_logs_result = pd.merge(self.interval_logs_result, self.manual_grades, on=['Assignment_id', 'User_id'])
        
        self.pattern_detection_result['User_id'] = self.pattern_detection_result['User_id'].astype(pd.Int64Dtype())

        self.interval_logs_result = pd.merge(self.interval_logs_result, self.pattern_detection_result, on=['Assignment_id', 'User_id'])
        
        self.interval_logs_result['PD_result'] = self.interval_logs_result['PD_result'].apply(lambda x: -1 if x=="Found" else 1)
        
        self.interval_logs_result['Final_score'] = self.interval_logs_result.apply(lambda x: self.computeFinalScore(x), axis=1)
        columns_to_delete = ['Team_id', 'Comments', 'Pattern', 'Repetition']
        self.interval_logs_result = self.interval_logs_result.drop(columns=columns_to_delete, axis=1)
        
        self.interval_logs_result["Grades"] = self.interval_logs_result["Grades"].apply(lambda x: self.convertToQuadrant(x))
        self.interval_logs_result["Final_score"] = self.interval_logs_result["Final_score"].apply(lambda x: self.convertToQuadrant(x))


        self.interval_logs_result.to_csv("final_result.csv", index=False)

        confusion_matrix = pd.crosstab(self.interval_logs_result['Grades'], self.interval_logs_result['Final_score'])

        print(confusion_matrix)
corr = Correlation()
corr.modifyAgreementDisagreemt()