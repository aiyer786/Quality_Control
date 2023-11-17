import argparse
import ast
from MySQL import MySQL
from collections import defaultdict
from TaggerClassifier import TaggerClassifier
from TagClassifier import TagClassifier
from PatternDetection_refactored import PatternDetection
import numpy as np
import pandas as pd
import os


class Application:
    """
    Master class of the Application
    """
    def __init__(self) -> None:
        self._connector = MySQL()                       # MySQL connector to call methods of MySQL class
        self.assignment_to_users = defaultdict(dict)    # dictionary to store the result of interval logs query
        self.tagger_classifier = TaggerClassifier()     # object of TaggerClassifier class
        self.tag_classifier = TagClassifier()           # object of TagClassifier class
        self.interval_logs_result = defaultdict(dict)   # result of interval logs
        self.krippendorff_result = defaultdict(dict)    # result of krippendorff alpha for a user
        self.agree_disagree_tags = defaultdict(dict)    # result of agreement/disagreement for each tag
        self.pattern_detection_result = defaultdict(dict) # result of interval logs
        self.assignment_to_user = defaultdict(dict)   
        self.pattern_detection = PatternDetection()
        self.assignment_to_teams = {}                  # dictionary that stores the result of getUserTeams function
        
    def __getIntervalLogs(self, tags, log_time=None) -> None:
        """
        Calculates Interval logs

        Args:
            tags (list): List of tags
        """
        # Populating the assignment_to_users hashmap based on the assignment_id and user_id
        for tag in tags:
            if tag.assignment_id in self.assignment_to_users:
                if tag.user_id in self.assignment_to_users[tag.assignment_id]:
                    self.assignment_to_users[tag.assignment_id][tag.user_id].append(tag)
                else:
                    self.assignment_to_users[tag.assignment_id][tag.user_id] = [tag]
            else:
                self.assignment_to_users[tag.assignment_id] = {tag.user_id: [tag]}
                
        # Calculating interval logs per assignment per user
        for assignment_id, users in self.assignment_to_users.items():
            for user,tags in users.items():
                self.interval_logs_result[assignment_id][user] = self.tagger_classifier.buildIntervalLogs(self.assignment_to_users[assignment_id][user])
        
        # Displaying the interval logs for a user per assignment
        # for assignment_id, users in self.interval_logs_result.items():
        #     for user in users:
        #         print('{},{},{}\n'.format(assignment_id, user, self.interval_logs_result[assignment_id][user]))
        
        # Writing the interval logs to a csv file if the log time is greater than the given log time
        f = open("data/Interval_logs.csv","w")
        f.write("Assignment_id,User_id,IL_result,Time,Number_of_Tags\n")
        for i in self.interval_logs_result:
            for j in self.interval_logs_result[i]:
                log_time_value=self.interval_logs_result[i][j][0]
                number_of_tags=self.interval_logs_result[i][j][1]
                if log_time is None or self.interval_logs_result[i][j] >= log_time:
                    f.write(str(i)+","+str(j)+","+str(log_time_value)+","+str(pow(2, log_time_value))+","+str(number_of_tags)+"\n")
        f.close()
    
    
    def __getKrippendorffAlpha(self, alpha=None):
        """
        Calculates krippendorf alpha value for each user
        """
        
        for assignment in self.assignment_to_teams:
            for team in self.assignment_to_teams[assignment].teams:
                data = []
                answers = defaultdict(set)
                users = []
                
                #collecting all the tag_prompt_ids for al answers of a team
                for user in self.assignment_to_teams[assignment].teams[team].users:
                    users.append(user)
                    for answer in self.assignment_to_teams[assignment].teams[team].users[user].answers:
                        for tag in self.assignment_to_teams[assignment].teams[team].users[user].answers[answer].tags:
                            answers[answer].add(tag)
                
                # collecting all the raters data for a single tag_prompt_id
                for answer in answers:
                    for tag in answers[answer]:
                        row = []
                        for user in self.assignment_to_teams[assignment].teams[team].users:
                            if answer not in self.assignment_to_teams[assignment].teams[team].users[user].answers:
                                row.append(np.nan)
                            elif tag not in self.assignment_to_teams[assignment].teams[team].users[user].answers[answer].tags:
                                row.append(np.nan)
                            else:
                                row.append(self.assignment_to_teams[assignment].teams[team].users[user].answers[answer].tags[tag].value)
                
                        data.append(row)
                if len(data[0])==1:
                    self.krippendorff_result[assignment][team] = {users[0]: np.nan}
                    continue
                data = np.array(data)
                
                #calculating krippendorff's alpha for all users in a team for an assignment
                self.krippendorff_result[assignment][team] = self.tagger_classifier.computeKrippendorffAlpha(data, users)
        
        #writing the krippendorff's alpha to a csv file if the alpha value is greater than the given alpha value
        f = open("data/krippendorff.csv", "w")
        f.write("Assignment_id,Team_id,User_id,Alphas\n")
        for i in self.krippendorff_result:
            for j in self.krippendorff_result[i]:
                for k in self.krippendorff_result[i][j]:
                    if alpha is None or self.krippendorff_result[i][j][k] >= alpha:
                        f.write(str(i)+","+str(j)+","+' '+str(k)+", "+str(self.krippendorff_result[i][j][k])+"\n")
        f.close()
     
    def __calculateAgreementDisagreement(self):
        for assignment in self.assignment_to_teams:
            for team in self.assignment_to_teams[assignment].teams:
                data = []
                answers = defaultdict(set)
                
                #collecting all the tag_prompt_ids for al answers of a team
                for user in self.assignment_to_teams[assignment].teams[team].users:
                    for answer in self.assignment_to_teams[assignment].teams[team].users[user].answers:
                        for tag in self.assignment_to_teams[assignment].teams[team].users[user].answers[answer].tags:
                            answers[answer].add(tag)
                
                # collecting all the raters data for a single tag_prompt_id
                for answer in answers:
                    for tag in answers[answer]:
                        row = []
                        for user in self.assignment_to_teams[assignment].teams[team].users:
                            if answer not in self.assignment_to_teams[assignment].teams[team].users[user].answers:
                                row.append(None)
                            elif tag not in self.assignment_to_teams[assignment].teams[team].users[user].answers[answer].tags:
                                row.append(None)
                            else:
                                row.append(self.assignment_to_teams[assignment].teams[team].users[user].answers[answer].tags[tag])
                
                        data.append(row)
                if len(data[0])==0:
                    self.agree_disagree_tags[assignment][team] = np.nan
                    continue
                data = np.array(data)
                
                #calculating agreement/disagreement of all tags
                self.agree_disagree_tags[assignment][team] = self.tag_classifier.calculateAgreementDisagreement(data)
        
        f = open("data/tags.csv","w")
        f.write("Assignment_id,team_id,answer_id,tag_prompt_id,value,fraction\n")
        for i in self.agree_disagree_tags:
            for j in self.agree_disagree_tags[i]:
                for k in self.agree_disagree_tags[i][j]:
                    for l in self.agree_disagree_tags[i][j][k]:
                        f.write(str(i)+","+str(j)+","+str(k)+","+str(l)+","+str(self.agree_disagree_tags[i][j][k][l][0])+","+str(self.agree_disagree_tags[i][j][k][l][1])+"\n")
        f.close()        
        
    def assignTaggerReliability(self, log_time=None, alpha=None, lmin=5, lmax=30, minrep=15):
        """
        Function used to compute Interval Logs, Krippendorff Alpha and Pattern detection
        """
        # Interval logs
        self.tags = self._connector.getAnswerTags()
        self.__getIntervalLogs(self.tags, log_time)
    
        # Krippendorff alpha
        self.assignment_to_teams = self._connector.getUserTeams()
        self.__getKrippendorffAlpha(alpha)

        # # Pattern Detection
        self.__getPatternResults(self.tags, lmin, lmax, minrep)

        
    def assignTagReliability(self):
        """
        Function used to compute Agreement/Disagreement of tags
        """
        self.__calculateAgreementDisagreement()

    def __getPatternResults(self, tags, lmin=5, lmax=30, minrep=15) -> None:
        """
        Calculates pattern detection results

        Args:
            tags (list): List of tags
        """
        # Populating the assignment_to_users hashmap based on the assignment_id and user_id
        for tag in tags:
            if tag.assignment_id in self.assignment_to_user:
                if tag.user_id in self.assignment_to_user[tag.assignment_id]:
                    self.assignment_to_user[tag.assignment_id][tag.user_id].append(tag)
                else:
                    self.assignment_to_user[tag.assignment_id][tag.user_id] = [tag]
            else:
                self.assignment_to_user[tag.assignment_id] = {tag.user_id: [tag]}
        
        # Calculating pattern detection results for each assignment and user
        for assignment_id, users in self.assignment_to_user.items():
            for user,tags in users.items():

                # Calculate pattern detection result using the PTV method with parameters 2, 6, and 2
                        self.pattern_detection_result[assignment_id][user] = self.pattern_detection.PTV(self.assignment_to_user[assignment_id][user],lmin,lmax,minrep)        
        

        # Writing the pattern detection results to a file
        f = open("data/Pattern_recognition.txt","w")
        f.write("Assignment_id/User_id/PD_result/Pattern/Repetition\n")
        for i in self.pattern_detection_result:
            for j in self.pattern_detection_result[i]:
                if self.pattern_detection_result[i][j][0]:
                    f.write(str(i)+"/"+str(j)+"/"+str(self.pattern_detection_result[i][j][2])+"/"+str(self.pattern_detection_result[i][j][0])+"/"+str(self.pattern_detection_result[i][j][1])+"\n")
                else:
                    f.write(str(i)+"/"+str(j)+"/"+str(self.pattern_detection_result[i][j][2])+"\n")
        f.close()
    
    def combine_csv_results(self, output_file):
        # Read the CSV files into DataFrames
        interval_logs_df = pd.read_csv("data/Interval_logs.csv")
        krippendorff_df = pd.read_csv("data/krippendorff.csv")
        pattern_results_df = pd.read_csv("data/Pattern_recognition.txt", sep="/", header=0, names=["Assignment_id", "User_id", "PD_result", "Pattern", "Repetition"])

        # Merge the DataFrames on 'Assignment_id' and 'User_id'
        merged_df = interval_logs_df.merge(krippendorff_df, on=['Assignment_id', 'User_id'])

        merged_df = merged_df.merge(pattern_results_df, on=['Assignment_id', 'User_id'])

        # Ensure the 'Time' column is present after the merge
        print(merged_df.columns)

        # Replace the 'Repetition' column values with 'Y' for 1 and 'N' for -1
        # Assuming merged_df is your DataFrame and 'Pattern' is the column of interest
        merged_df['Pattern'] = merged_df['Pattern'].apply(lambda x: x.replace('-1', 'N').replace('1', 'Y') if isinstance(x, str) else x)

        # If you want to ensure that 'N/A' values are left as they are, you could add a condition:
        merged_df['Pattern'] = merged_df['Pattern'].apply(lambda x: x.replace('-1', 'N').replace('1', 'Y') if isinstance(x, str) and x != 'N/A' else x)


        # Now select the columns, ensuring each column name is a separate string in the list
        final_df = merged_df[['User_id', 'Assignment_id', 'Team_id', 'IL_result', 'Time', 'Alphas', 'PD_result', "Pattern", "Repetition", "Number_of_Tags"]]
        final_df.columns = ['USER ID', 'ASSIGNMENT ID', 'TEAM ID', 'FAST TAGGING LOG VALUES', 'FAST TAGGING SECONDS', 'ALPHA VALUES', 'PATTERN FOUND OR NOT', 'PATTERN', 'PATTERN REPETITION', 'NUMBER OF TAGS']

        # Replace NaNs with a more descriptive value, if necessary
        final_df.fillna('N/A', inplace=True)

        # Write the combined results to a new CSV file
        output_path = f"data/{output_file}"
        final_df.to_csv(output_path, index=False)

        print(f"Combined CSV created successfully as {output_path}")



if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    parser = argparse.ArgumentParser(description="Run the Application with specific parameters.")
    parser.add_argument('--log_time_min', type=float, default=None, help="Filtering value for log time.")
    parser.add_argument('--alpha_min', type=float, default=None, help="Filtering value for krippendorff alpha.")
    parser.add_argument('--min_pattern_len', type=int, default=5, help="Minimum value for pattern detection.")
    parser.add_argument('--max_pattern_len', type=int, default=30, help="Maximum value for pattern detection.")
    parser.add_argument('--min_pattern_rep', type=int, default=15, help="Minimum repetition value for pattern detection.")
    args = parser.parse_args()

    app = Application()
    app.assignTaggerReliability(args.log_time_min, args.alpha_min, args.min_pattern_len, args.max_pattern_len, args.min_pattern_rep)
    app.combine_csv_results('Combined_Results.csv')
