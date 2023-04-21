from MySQL import MySQL
from collections import defaultdict
from TaggerClassifier import TaggerClassifier
from TagClassifier import TagClassifier
from PatternDetection_refactored import PatternDetection
import numpy as np

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
        self.assignement_to_teams = {}                  # dictionary that stores the result of getUserTeams function
        self.pattern_detection_result = defaultdict(dict) # result of interval logs
        self.assignment_to_user = defaultdict(dict)   
        self.pattern_detection = PatternDetection()
        
    def __getIntervalLogs(self, tags) -> None:
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
                self.interval_logs_result[assignment_id][user] = self.tagger_classifier.intervalLogs(self.assignment_to_users[assignment_id][user])
        
        # Displaying the interval logs for a user per assignment
        # for assignment_id, users in self.interval_logs_result.items():
        #     for user in users:
        #         print('{},{},{}\n'.format(assignment_id, user, self.interval_logs_result[assignment_id][user]))
        
        f = open("Interval_logs","w")
        f.write("Assignment_id,User_id,IL_result\n")
        for i in self.interval_logs_result:
            for j in self.interval_logs_result[i]:
                f.write(str(i)+","+str(j)+","+str(self.interval_logs_result[i][j])+"\n")
        f.close()
    
    def __calculateKrippendorffAlpha(self):
        """
        Calculates krippendorf alpha value for each user
        """
        
        for assignment in self.assignement_to_teams:
            for team in self.assignement_to_teams[assignment].teams:
                data = []
                answers = defaultdict(set)
                
                #collecting all the tag_prompt_ids for al answers of a team
                for user in self.assignement_to_teams[assignment].teams[team].users:
                    for answer in self.assignement_to_teams[assignment].teams[team].users[user].answers:
                        for tag in self.assignement_to_teams[assignment].teams[team].users[user].answers[answer].tags:
                            answers[answer].add(tag)
                
                # collecting all the raters data for a single tag_prompt_id
                for answer in answers:
                    for tag in answers[answer]:
                        row = []
                        for user in self.assignement_to_teams[assignment].teams[team].users:
                            if answer not in self.assignement_to_teams[assignment].teams[team].users[user].answers:
                                row.append(np.nan)
                            elif tag not in self.assignement_to_teams[assignment].teams[team].users[user].answers[answer].tags:
                                row.append(np.nan)
                            else:
                                row.append(self.assignement_to_teams[assignment].teams[team].users[user].answers[answer].tags[tag].value)
                
                        data.append(row)
                if len(data[0])==1:
                    self.krippendorff_result[assignment][team] = [np.nan]
                    continue
                data = np.array(data)
                
                #calculating krippendorff's alpha for all users in a team for an assignment
                self.krippendorff_result[assignment][team] = self.tagger_classifier.getKrippendorffAlpha(data)
        
        f = open("krippendorff.csv", "w")
        f.write("Assignment_id,team_id,Alphas\n")
        for i in self.krippendorff_result:
            for j in self.krippendorff_result[i]:
                f.write(str(i)+","+str(j)+","+' '.join(map(str,self.krippendorff_result[i][j]))+"\n")
        f.close()
     
    def __calculateAgreementDisagreement(self):
        for assignment in self.assignement_to_teams:
            for team in self.assignement_to_teams[assignment].teams:
                data = []
                answers = defaultdict(set)
                
                #collecting all the tag_prompt_ids for al answers of a team
                for user in self.assignement_to_teams[assignment].teams[team].users:
                    for answer in self.assignement_to_teams[assignment].teams[team].users[user].answers:
                        for tag in self.assignement_to_teams[assignment].teams[team].users[user].answers[answer].tags:
                            answers[answer].add(tag)
                
                # collecting all the raters data for a single tag_prompt_id
                for answer in answers:
                    for tag in answers[answer]:
                        row = []
                        for user in self.assignement_to_teams[assignment].teams[team].users:
                            if answer not in self.assignement_to_teams[assignment].teams[team].users[user].answers:
                                row.append(None)
                            elif tag not in self.assignement_to_teams[assignment].teams[team].users[user].answers[answer].tags:
                                row.append(None)
                            else:
                                row.append(self.assignement_to_teams[assignment].teams[team].users[user].answers[answer].tags[tag])
                
                        data.append(row)
                if len(data[0])==0:
                    self.agree_disagree_tags[assignment][team] = np.nan
                    continue
                data = np.array(data)
                
                #calculating agreement/disagreement of all tags
                self.agree_disagree_tags[assignment][team] = self.tag_classifier.calculateAgreementDisagreement(data)
        
        f = open("tags.csv","w")
        f.write("Assignment_id,team_id,answer_id,tag_prompt_id,value,fraction\n")
        for i in self.agree_disagree_tags:
            for j in self.agree_disagree_tags[i]:
                for k in self.agree_disagree_tags[i][j]:
                    for l in self.agree_disagree_tags[i][j][k]:
                        f.write(str(i)+","+str(j)+","+str(k)+","+str(l)+","+str(self.agree_disagree_tags[i][j][k][l][0])+","+str(self.agree_disagree_tags[i][j][k][l][1])+"\n")
        f.close()        
        
    def assignTaggerReliability(self):
        """
        Function used to compute Interval Logs, Krippendorff Alpha and Pattern detection
        """
        # # Interval logs
        tags = self._connector.getAnswerTags()
        self.__getIntervalLogs(tags)
    
        # Krippendorff alpha
        self.assignement_to_teams = self._connector.getUserTeams()
        self.__calculateKrippendorffAlpha()
        
    def assignTagReliability(self):
        """
        Function used to compute Agreement/Disagreement of tags
        """
        self.__calculateAgreementDisagreement()

    def __getPatternResults(self, tags) -> None:
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
        
        for assignment_id, users in self.assignment_to_user.items():
            for user,tags in users.items():
                self.pattern_detection_result[assignment_id][user] = self.pattern_detection.PTV(self.assignment_to_user[assignment_id][user])
        


app = Application()
app.assignTaggerReliability()
app.assignTagReliability()
    
    