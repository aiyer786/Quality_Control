import argparse
import ast
import re
from MySQL import MySQL
from collections import defaultdict
from TaggerClassifier import TaggerClassifier
from TagClassifier import TagClassifier
from PatternDetection_refactored import PatternDetection
import numpy as np
import pandas as pd
import os
import csv
import ast

class Application: 
    """
     Master class of the Application, integrating various modules for processing crowd-labeled data 
    and performing quality control tasks such as speed-based tagging analysis, 
    inter-rater reliability (Krippendorff's alpha), tag credibility assessment, and pattern detection.
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
        self.user_history_dict = defaultdict(dict)
        self.pattern_detection = PatternDetection()
        self.assignment_to_teams = {}                  # dictionary that stores the result of getUserTeams function
        
    def __getIntervalLogs(self, tags, log_time=None) -> None:
        """
         Calculates interval log values for each user, which are used to evaluate how quickly users assigned tags.
        Helps identify users who might have tagged "too fast," indicating potentially unreliable data.

        - **Interval Log Calculation**:
          For each user, this method calculates:
          * Time intervals between consecutive tags.
          * Log base 2 transformation of these intervals to reduce the effect of large gaps.
          * Average log interval time for each user.

        - **Credibility Implication**:
          Users with a very low average log interval time might have tagged too quickly, suggesting poor quality.

        Writes results to a CSV:
        - `Assignment_id`: Assignment to which the user belongs.
        - `User_id`: User who assigned the tags.
        - `IL_result`: Average log of interval times.
        - `Time`: Derived time spent tagging from interval logs (converted back from log).
        - `Number_of_Tags`: Total number of tags assigned by the user.

        Args:
            tags (list): List of tags fetched from the database (list of `AnswerTag` objects).
            log_time (float, optional): Minimum acceptable log time; users with lower values are excluded.  

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
                
        with open("data/Interval_logs.csv", "w") as f:
            f.write("Assignment_id,User_id,IL_result,Time,Number_of_Tags\n")
            for assignment_id, users in self.interval_logs_result.items():
                for user_id, results in users.items():
                    log_time_value = results[0]
                    number_of_tags = results[1]
                    if log_time is None or log_time_value >= log_time:
                        # Format IL_result and Time to 3 decimal places
                        il_result_formatted = "{:.3f}".format(log_time_value)
                        time_formatted = "{:.3f}".format(pow(2, log_time_value))
                        f.write(f"{assignment_id},{user_id},{il_result_formatted},{time_formatted},{number_of_tags}\n")
        print("Interval logs written to data/Interval_logs.csv")
        f.close()
    
    def __getUserHistory(self, user_history) -> None:
        """
        Processes user tagging history, calculates tag credibility scores, 
        and writes the results to a CSV.

        - **Credibility Score Calculation**:
          * Combines fast tagging log values with Krippendorff's alpha to assess tag reliability.
          * Tags with high credibility scores are deemed more reliable.
          * Credibility score normalization ensures fair comparisons across multiple users:
            Normalized log time and normalized alpha are averaged to determine reliability.
        Args:
            user_history (list): List of user tags fetched from the database.
        """         
        # Populate user_history_dict
        for tag in user_history:
            if tag.assignment_id in self.user_history_dict:
                if tag.user_id in self.user_history_dict[tag.assignment_id]:
                    self.user_history_dict[tag.assignment_id][tag.user_id].append(tag)
                else:
                    self.user_history_dict[tag.assignment_id][tag.user_id] = [tag]
            else:
                self.user_history_dict[tag.assignment_id] = {tag.user_id: [tag]}

        # Calculate credibility scores for tags
        credibility_scores = self.tagger_classifier.calculate_tag_credibility_score(user_history)

        # Writing data to CSV with credibility scores
        with open("data/user_data.csv", "w") as f:
            f.write("User_id,Assignment_id,Question,Score,Review_Comment,Tag_Prompt,Tag_Value,Credibility_Score\n")
            for assignment_id, users in self.user_history_dict.items():
                for user, tags in users.items():                    
                    for tag in tags:
                        # Clean 'question' and 'comments' by removing HTML tags and commas
                        cleaned_question = re.sub('<.*?>', '', tag.question).replace(',', '').replace('\n', '').replace('\r', '')
                        cleaned_comments = re.sub('<.*?>', '', tag.comments).replace(',', '').replace('\n', '').replace('\r', '')
                        
                        # Get credibility score for the tag
                        tag_credibility_score = credibility_scores.get(tag.id, 0)

                        # Concatenate the cleaned strings with other information and add it to the output string
                        output_string = f"{str(user)},{str(assignment_id)},{cleaned_question},{tag.answer_score},{cleaned_comments},{tag.prompt},{tag.value},{tag_credibility_score}\n"
                        f.write(output_string)

            print("User data with credibility scores written to data/user_data.csv")
  
    def __getStudentsWhoTagged(self):

        """
         Analyzes student participation by calculating the number of unique users who tagged each question.

        **Use Case**:
        Helpful for understanding how many diverse opinions contributed to tagging specific questions.
        
        **Metrics**:
        Groups data by questions and counts distinct user IDs for each question.

        Writes results to a CSV (`data/number_of_students_who_tagged_each_question.csv`):
        - `Question`: The question being tagged.
        - `Unique_User_Count`: Count of unique users who tagged that question.

        """

        # Read the CSV data into a pandas DataFrame
        df = pd.read_csv(("data/user_data.csv"), encoding='cp1252')

        # Group by 'Question' and count unique 'User_id's
        unique_users_per_question = df.groupby('Question')['User_id'].nunique()

        # Convert the result to a DataFrame for easier CSV export
        result_df = unique_users_per_question.reset_index()
        result_df.columns = ['Question', 'Unique_User_Count']

        # Save the result to a new CSV file
        output_file = 'number_of_students_who_tagged_each_question.csv'

        # Write the combined results to a new CSV file
        output_path = f"data/{output_file}"
        result_df.to_csv(output_path, index=False, na_rep=' ',  quoting=csv.QUOTE_MINIMAL)

        print("Results saved to 'number_of_students_who_tagged_each_question.csv'")

    def __getKrippendorffAlpha(self, alpha=None):
            """
            Computes Krippendorff's alpha to measure inter-rater reliability (IRR) within teams.

            - **Purpose**:
            Assesses the consistency of taggers in a team by analyzing agreements on assigned tag values.
            Alpha ranges from -1 (complete disagreement) to 1 (perfect agreement).

            - **Process**:
            - Builds a matrix where rows = tagged items, columns = users, values = tag values.
            - Uses the matrix to calculate alpha for each team or user.

            - **Output**:
            Writes `Assignment_id`, `Team_id`, `User_id`, and `Alphas` to `data/krippendorff.csv`.

            Args:
                alpha (float, optional): Minimum acceptable alpha for filtering. Defaults to None.
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
        for assignment_id, teams in self.krippendorff_result.items():
            for team_id, users_alphas in teams.items():
                for user_id, alpha_value in users_alphas.items():
                    # Check if alpha is None or the alpha value is greater or equal than the given alpha threshold
                    if alpha is None or alpha_value >= alpha:
                        # Format Alphas to 3 decimal places if it's a float, otherwise write 'nan'
                        alpha_formatted = "{:.3f}".format(alpha_value) if isinstance(alpha_value, float) else "nan"
                        f.write(f"{assignment_id},{team_id},{user_id},{alpha_formatted}\n")
        print("Krippendorff's alpha written to data/krippendorff.csv")
        f.close()
     
    def __calculateAgreementDisagreement(self):
        """
        Computes agreement/disagreement among taggers based on the consensus for tag values.

        - **Metrics**:
          For each tag, calculates:
          1. Dominant value assigned to a tag (e.g., `1` or `-1`).
          2. Fraction indicating the level of agreement among users for that value.
          High fraction values indicate agreement; lower values suggest disagreement.

        Writes results to a CSV (`tags.csv`):
        - `Assignment_id`, `team_id`, `answer_id`, `tag_prompt_id`
        - `value`: Dominant tag value.
        - `fraction`: Agreement fraction for the tag value.

        """
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
    Executes the pipeline to evaluate tagger reliability by combining several analyses:
      1. **Interval Logs**: Measures tagging speed (log transformations of time gaps).
      2. **Krippendorff Alpha**: Assesses inter-rater agreement to evaluate tag consistency.
      3. **Pattern Detection**: Detects repetitive tagging behavior (defined by pattern length and repetitions).
      4. **Credibility Scores**: Combines metrics to quantify individual tagger reliability.

    Args:
        log_time (float): Minimum threshold for interval log time.
        alpha (float): Minimum team consistency alpha.
        lmin (int), lmax (int): Min/max pattern lengths for detection.
        minrep (int): Minimum repetitions to qualify a pattern.
    """
        # Interval logs
        self.tags = self._connector.getAnswerTags()
        self.__getIntervalLogs(self.tags, log_time)
    
        # Krippendorff alpha
        self.assignment_to_teams = self._connector.getUserTeams()
        self.__getKrippendorffAlpha(alpha)

        # # Pattern Detection
        self.__getPatternResults(self.tags, lmin, lmax, minrep)

        # User data
        self.user_history = self._connector.getUserHistory()
        self.__getUserHistory(self.user_history)

        #Number of students who tagged each question
        self.__getStudentsWhoTagged()
        
    def assignTagReliability(self):
        """
        Function used to compute Agreement/Disagreement of tags
        """
        self.__calculateAgreementDisagreement()



    def find_long_consecutiveY(self, string):
    """
    Finds sequences of at least 10 consecutive 'Y's (yes tags) in the tagging history.

    - **Purpose**:
      Detects repetitive, predictable sequences in 'Y' tags, which may indicate biased tagging behavior.

    Args:
        string (dict): A dictionary containing a "Tags" string with 'Y'/'N' values.

    Returns:
        list: Lengths of 'Y' sequences where length > 10.
    """
        substrings = []
        current_length = 0
        for c in string["Tags"]:
            if c == 'Y':
                current_length += 1
            else:
                if current_length >= 10:
                    substrings.append(current_length)
                current_length = 0
        # Check the last substring
        if current_length > 10:
            substrings.append(current_length)

        return substrings

    def find_long_consecutiveN(self, string):
    """
    Finds sequences of at least 10 consecutive 'N's (no tags) in the tagging history.

    - **Purpose**:
      Identifies long runs of 'N' tags, potentially exposing tagging irregularities or patterns.

    Args:
        string (dict): Dictionary with a "Tags" string containing 'Y'/'N' values.

    Returns:
        list: Lengths of 'N' sequences where length > 10.
    """
        substrings = []
        current_length = 0
        for c in string["Tags"]:
            if c == 'N':
                current_length += 1
            else:
                if current_length > 10:
                    substrings.append(current_length)
                current_length = 0
        # Check the last substring
        if current_length > 10:
            substrings.append(current_length)

        return substrings

    def replace(self, tag_list):
    """
    Converts raw tag data into a cleaned format by mapping:
      - `1` -> 'Y', `-1` -> 'N', and removing all other values.

    - **Purpose**:
      Prepares tag data for analysis by normalizing inconsistent or irrelevant values.

    Args:
        tag_list (str): String representation of tags (e.g., "[1, -1, 1]").

    Returns:
        list: A cleaned list of 'Y' and 'N' values.
    """

        # Convert the string representation of a list to an actual list
        tag_list = ast.literal_eval(tag_list)

        # Replace '1' with 'Y' and '-1' with 'N', and remove all other elements
        tag_list = ['Y' if tag == '1' else 'N' if tag == '-1' else None for tag in tag_list]
        tag_list = [tag for tag in tag_list if tag is not None]

        return tag_list
    
    def find_Ys_Ns(self, tags_file_path):

            """
            Processes tag data from a CSV file to identify repetitive patterns of 'Y's and 'N's.

            - **Actions**:
            - Reads and cleans the "Tags" column.
            - Calculates the longest sequences of consecutive 'Y's and 'N's.
            - Records totals of repetitive patterns.

            - **Output**:
            Writes longest sequence information to `data/Longest_Y_N.csv`.

            Args:
                tags_file_path (str): Path to the CSV containing raw tag data.
            """
        # Read the CSV file
        df = pd.read_csv(tags_file_path)

        df['Tags'] = df['Tags'].apply(self.replace)
        df['Tags'] = df['Tags'].apply(lambda x: eval(x) if isinstance(x, str) else x)
        df['Consecutive Ys Pattern Count'] = ''
        df['Consecutive Ns Pattern Count'] = ''
        df['Consecutive Ys Pattern Count'] = df.apply(self.find_long_consecutiveY, axis = 1)
        df['Consecutive Ns Pattern Count'] = df.apply(self.find_long_consecutiveN, axis = 1)
        df['Total Repeating Ys'] = df['Consecutive Ys Pattern Count'].apply(lambda arr: int(np.sum(arr)))
        df['Total Repeating Ns'] = df['Consecutive Ns Pattern Count'].apply(lambda arr: int(np.sum(arr)))

        df.to_csv('data/Longest_Y_N.csv', index = False)
        print("Consecutive Ys and Ns Pattern results written to 'data/Longest_Y_N.csv'")



    def __getPatternResults(self, tags, lmin=5, lmax=30, minrep=15) -> None:
        """
        Performs pattern detection to identify repetitive sequences in user tagging behaviors.

        - **Actions**:
        - Searches for patterns (e.g., repeating 'YYN') with lengths between `lmin` and `lmax`.
        - Includes patterns that occur at least `minrep` times.

        - **Output**:
        Writes pattern results (`Assignment_id`, `User_id`, `Pattern`, `Repetitions`) to a summary file.

        Args:
            tags (list): Tag data to analyze.
            lmin (int): Minimum pattern length.
            lmax (int): Maximum pattern length.
            minrep (int): Minimum repetitions for a valid pattern.
        """
        # Populating the assignment_to_users hashmap
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
            user_df = pd.DataFrame(columns = ["User", "Tags"])
            for user, tags in users.items():
                

                temp_tags = tags
                temp_tags.sort(key=lambda l: l.created_at)
                temp_bin_data = [i.value for i in temp_tags]
                temp_user = pd.DataFrame({"User": user, "Tags": [temp_bin_data]})
                user_df = pd.concat([user_df, temp_user], ignore_index=True)


                pattern_results = self.pattern_detection.PTV(tags, lmin, lmax, minrep)
                self.pattern_detection_result[assignment_id][user] = pattern_results

            user_df.to_csv("data/user_tags.csv", index=False)
            print("User Tags are written to 'data/user_tags.csv'")
        
        self.find_Ys_Ns("data/user_tags.csv")
        
        # Writing the pattern detection results to a file
        with open("data/Pattern_recognition.txt", "w") as f:
            f.write("Assignment_id/User_id/PD_result/Pattern/Repetition\n")
            for assignment_id, users in self.pattern_detection_result.items():
                for user, patterns in users.items():
                    for pattern, count in patterns:
                        if pattern != "Not_found":
                            f.write(f"{assignment_id}/{user}/Found/{pattern}/{count}\n")
                        else:
                            f.write(f"{assignment_id}/{user}/Not_found\n")
        print("Pattern recognition results written to data/Pattern_recognition.txt")
    
    def calculate_credibility(self, log_time, alpha, total_characters, log_time_max, alpha_max, characters_max):
            """
            Calculates a credibility score for a tagger based on three metrics:
            1. **Tagging Speed**: Normalized log time of tag intervals.
            2. **Inter-Rater Reliability**: Normalized Krippendorff's alpha.
            3. **Tag Complexity**: Penalizes overly repetitive or simple patterns.

            - **Credibility Formula**:
            Credibility = (Norm_Log_Time + Norm_Alpha + Norm_Tag_Complexity) / 3

            Args:
                log_time (float): Log time of intervals between tags.
                alpha (float): Krippendorff's alpha for agreement reliability.
                total_characters (float): Total tag sequence length contributed by this user.
                log_time_max (float): Maximum observed log time.
                alpha_max (float): Maximum observed alpha.
                characters_max (float): Maximum observed tag length.

            Returns:
                float: Credibility score in the range [0, 1].
            """

        # Check and handle non-numeric or missing values
        log_time = 0 if not isinstance(log_time, (int, float)) or pd.isna(log_time) else log_time
        alpha = 0 if not isinstance(alpha, (int, float)) or pd.isna(alpha) else alpha
        total_characters = 0 if not isinstance(total_characters, (int, float)) or pd.isna(total_characters) else total_characters

        normalized_log_time = log_time / log_time_max if log_time_max != 0 else 0
        normalized_alpha = alpha / alpha_max if alpha_max != 0 else 0
        normalized_characters = 1 - (total_characters / characters_max if characters_max != 0 else 0)
        
        credibility = (normalized_log_time + normalized_alpha + normalized_characters) / 3
        return round(credibility, 5)
    


    def remove_indices_smaller(self, pattern, rep):
        """
        Filters out patterns with insufficient diversity (fewer than 2 unique elements).

        - **Purpose**:
        Ensures only meaningful tag patterns are included in analysis by removing overly simplistic patterns.

        Args:
            pattern (list): List of patterns detected.
            rep (list): List of repetition counts for corresponding patterns.

        Returns:
            list: Filtered list of valid patterns.
        """
        indices_to_remove = [i for i, p in enumerate(pattern) if len(set(p))<2]
        return [r for i, r in enumerate(rep) if i not in indices_to_remove]

    def update_results(self, path):
        df = pd.read_csv(path)
        df['Pattern'] = df['Pattern'].fillna(df['Pattern'].apply(lambda x: []))
        df['Pattern Repetition'] = df['Pattern Repetition'].fillna(df['Pattern Repetition'].apply(lambda x: []))
        df['Pattern Repetition'] = df['Pattern Repetition'].apply(lambda x: eval(x) if isinstance(x, str) else x)
        df['Pattern'] = df['Pattern'].apply(lambda x: eval(x) if isinstance(x, str) else x)
        df['Pattern Repetition'] = df.apply(lambda row: self.remove_indices_smaller(row['Pattern'], row['Pattern Repetition']), axis=1)
        df['Pattern'] = df['Pattern'].apply(lambda x:[item for item in x if len(set(item)) > 1])
        df['Total Repeating Characters'] = df['Pattern Repetition'].apply(lambda arr: int(np.sum(arr)))
        
        # Check for pattern existence and create new column
        df['Pattern Found or Not'] = df['Pattern'].apply(lambda patterns: 'Found' if any(patterns) else 'Not Found')
    
        return df

    def process_and_save_final_results(self, results_filename, longest_yn_filename, output_filename):
            """
            Merges results from multiple tagging analyses into a final summary.

            - **Inputs**:
            Combines interval logs, Krippendorff alpha, and pattern analysis results.

            - **Output**:
            Saves a formatted CSV file containing user performance summaries.

            Args:
                results_filename (str): File with tagging performance results.
                longest_yn_filename (str): File with longest 'Y'/'N' patterns.
                output_filename (str): Final output file path.
            """
            # Read CSV files
            long_y_n = pd.read_csv(longest_yn_filename)
            df = pd.read_csv(results_filename)
            
            # Merge DataFrames
            merged_df = df.merge(long_y_n, left_on='User ID', right_on='User')
            
            # Reorder columns and rename Credibility column
            cred_column = merged_df.pop("Credibility")
            merged_df["Credibility"] = cred_column
            merged_df.drop(columns=["User", "Tags"], inplace=True)

            # Save to CSV
            merged_df.to_csv(output_filename, index=False)

            print(f"Final file combining all the results is written at {output_filename}")



    def combine_csv_results(self, output_file):
        """
        Generates a master CSV by merging intermediate analysis outputs like interval logs,
        agreement scores, and pattern results.

        **Purpose**:
        Provides a comprehensive summary of tagging quality for all users.

        Args:
        output_file (str): Path to save the final combined CSV.
        """
        # Read the CSV files into DataFrames
        interval_logs_df = pd.read_csv("data/Interval_logs.csv")
        krippendorff_df = pd.read_csv("data/krippendorff.csv")
        pattern_results_df = pd.read_csv("data/Pattern_recognition.txt", sep="/", header=0, names=["Assignment_id", "User_id", "PD_result", "Pattern", "Repetition"])

        # Merge the DataFrames on 'Assignment_id' and 'User_id'
        merged_df = interval_logs_df.merge(krippendorff_df, on=['Assignment_id', 'User_id'])
        merged_df = merged_df.merge(pattern_results_df, on=['Assignment_id', 'User_id'])

        # Ensure the 'Time' column is present after the merge
        print(merged_df.columns)

        # Replace 'N/A' with a space in the entire DataFrame
        merged_df.replace('N/A', ' ', inplace=True)
        
        # Replace '-1' with a space in the 'Fast Tagging Log Values' column
        merged_df['IL_result'] = merged_df['IL_result'].apply(lambda x: ' ' if x == -1 else x)

        # Replace pattern strings like "('-1', '1', '1', '-1', '1', '1')" with "NYYNYY"
        merged_df['Pattern'] = merged_df['Pattern'].apply(
            lambda x: ''.join(['Y' if num == '1' else 'N' for num in ast.literal_eval(x)]) 
                    if isinstance(x, str) and x.startswith('(') else x
        )
            
        # Adding the 'Number of Tags Available' column using 'team_id'
        merged_df['Number_of_Tags_Available'] = merged_df['Team_id'].apply(lambda team_id: self._connector.getAnswerCount(team_id))


        # Adjust the column order and rename as needed
        merged_df = merged_df[['User_id', 'Assignment_id', 'Team_id', 'IL_result', 'Time', 'Alphas', "Number_of_Tags", "Number_of_Tags_Available",  'PD_result', 'Pattern', 'Repetition']]
        merged_df.columns = ['User ID', 'Assignment ID', 'Team ID', 'Fast Tagging Log Values', 'Fast Tagging Seconds', 'Alpha Values', 'Number of Tags Set', 'Number of Tags Available', 'Pattern Found or Not', 'Pattern', 'Pattern Repetition']

        #Ensuring that patterns of a single user appear in the same line
        agg_funcs = {'Assignment ID': 'min','Team ID':'min','Fast Tagging Log Values' :'min', 'Fast Tagging Seconds':'min','Alpha Values':'min','Number of Tags Set':'min',
             'Number of Tags Available':'min','Pattern Found or Not':'first', 'Pattern': lambda x: x.tolist(),'Pattern Repetition': lambda x: x.tolist()}
        # Group by 'id' and aggregate selected columns
        result_df = merged_df.groupby('User ID', as_index=False).agg(agg_funcs)

        #removing 'nan' values for users where no pattern was found
        rows_not_found = result_df[result_df['Pattern Found or Not'] == 'Not_found'].index
        columns_to_blank = ['Pattern', 	'Pattern Repetition']  
        result_df.loc[rows_not_found, columns_to_blank] = ''

        #removing single quotes for each pattern found inside the array
        result_df['Pattern'] = result_df['Pattern'].replace({'["\']': ''}, regex=True) 

        #function that calculates the result of pattern length * pattern repetition
        def calculate_score(row):
            # Split the columns
            patterns = row['Pattern']
            repetitions = row['Pattern Repetition']

            # Check if 'Pattern' and 'Pattern Repetition' are not None and not empty lists
            if patterns is not None and repetitions is not None and patterns and repetitions:
                total_score = sum(len(pattern) * repetition for pattern, repetition in zip(patterns, repetitions))
                return total_score if total_score != 0 else None
            else:
                return None        

        # Apply the function 
        result_df['Total Repeating Characters'] = result_df.apply(calculate_score, axis=1)

        # Handling any Nan values or cases where no pattern is found
        rows = result_df[result_df['Pattern Found or Not'] == 'Not_found'].index
        result_df.loc[rows, 'Total Repeating Characters'] = 0  # Set to 0 instead of empty string


         # Find the maximum values for normalization
        log_time_max = result_df['Fast Tagging Seconds'].max()
        alpha_max = result_df['Alpha Values'].max()
        characters_max = result_df['Total Repeating Characters'].max()

        # Calculate credibility for each row
        result_df['Credibility'] = result_df.apply(lambda row: self.calculate_credibility(
            row['Fast Tagging Seconds'], row['Alpha Values'], row['Total Repeating Characters'],
            log_time_max, alpha_max, characters_max
        ), axis=1)

        # Adjust the column order and rename as needed
        result_df = result_df[['User ID', 'Assignment ID', 'Team ID', 'Fast Tagging Log Values', 'Fast Tagging Seconds', 'Alpha Values', 'Number of Tags Set', 'Number of Tags Available', 'Pattern Found or Not', 'Pattern', 'Pattern Repetition','Total Repeating Characters', 'Credibility']]

        # Write the combined results to a new CSV file
        output_path = f"data/{output_file}"
        result_df.to_csv(output_path, index=False, na_rep=' ')

        # Update the result files for non-consecutive patterns
        result_df = self.update_results(output_path)
        result_df.to_csv(output_path, index=False, na_rep=' ')


        print(f"Combined CSV created successfully as {output_path}")

        self.process_and_save_final_results("data/Combined_Results.csv", "data/Longest_Y_N.csv", "data/1166_Tagger_Results.csv")


if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)
    parser = argparse.ArgumentParser(description="Run the Application with specific parameters.")
    parser.add_argument('--log_time_min', type=float, default=None, help="Filtering value for log time.")
    parser.add_argument('--alpha_min', type=float, default=None, help="Filtering value for krippendorff alpha.")
    parser.add_argument('--min_pattern_len', type=int, default=10, help="Minimum value for pattern detection.")
    parser.add_argument('--max_pattern_len', type=int, default=50, help="Maximum value for pattern detection.")
    parser.add_argument('--min_pattern_rep', type=int, default=15, help="Minimum repetition value for pattern detection.")
    args = parser.parse_args()

    app = Application()
 
    app.assignTaggerReliability(args.log_time_min, args.alpha_min, args.min_pattern_len, args.max_pattern_len, args.min_pattern_rep)
    app.combine_csv_results('Combined_Results.csv')
