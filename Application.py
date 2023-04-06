from MySQL import MySQL
from collections import defaultdict
from TaggerClassifier import TaggerClassifier
import numpy as np

class Application:
    """
    Master class of the Application
    """
    def __init__(self) -> None:
        self._connector = MySQL()       # MySQL connector to call methods of MySQL class
        self.assignment_to_users = defaultdict(dict)    # hashmap of {assignment_id: {user_id: list(answer_tags)}}
        self.tc = TaggerClassifier()                    # object of TaggerClassifier
        self.intervals = defaultdict(dict)              # (displaying purpose) hashmap of {assignment_id: {user_id: interval_logs_result}}
        self.alphas = defaultdict(dict)
        
    def __getIntervalLogs(self, tags):
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
                #print(assignment_id, user)
                self.intervals[assignment_id][user] = self.tc.intervalLogs(self.assignment_to_users[assignment_id][user])
        
        # Displaying the interval logs for a user per assignment
        # for assignment_id, users in self.intervals.items():
        #     for user in users:
        #         print('{},{},{}\n'.format(assignment_id, user, self.intervals[assignment_id][user]))
            
    
    def __calculateKrippendorffAlpha(self, assignment_to_teams):
        for assignment in assignment_to_teams:
            for team in assignment_to_teams[assignment].teams:
                data = []
                answers = defaultdict(set)
                for user in assignment_to_teams[assignment].teams[team].users:
                    for answer in assignment_to_teams[assignment].teams[team].users[user].answers:
                        for tag in assignment_to_teams[assignment].teams[team].users[user].answers[answer].tags:
                            answers[answer].add(tag)
                
                #print(answers)
                for answer in answers:
                    for tag in answers[answer]:
                        row = []
                        for user in assignment_to_teams[assignment].teams[team].users:
                            if answer not in assignment_to_teams[assignment].teams[team].users[user].answers:
                                row.append(np.nan)
                            elif tag not in assignment_to_teams[assignment].teams[team].users[user].answers[answer].tags:
                                row.append(np.nan)
                            else:
                                row.append(assignment_to_teams[assignment].teams[team].users[user].answers[answer].tags[tag].value)
                
                        #print(row)
                        data.append(row)
                if len(data[0])==1:
                    self.alphas[assignment][team] = np.nan
                    continue
                data = np.array(data)
                self.alphas[assignment][team] = self.tc.getKrippendorffAlpha(data)
                #print(self.alphas)
        print(self.alphas)
                    
                    
    def assignTaggerReliability(self):
        """
        Currently checks for fast tagging by calling interval logs method
        Assigns reliability per assignment per user
        """
        # Fetching the answer tags from the database
        tags = self._connector.getAnswerTags()
        self.__getIntervalLogs(tags)
    
        assignment_to_teams = self._connector.getUserTeams()
        self.__calculateKrippendorffAlpha(assignment_to_teams)
        print(self.teams[33444].assignments[1026].answers[1422933].users[8975].tags[1].value)

app = Application()
app.assignTaggerReliability()
#app.test_users()       
    
    