from MySQL import MySQL
from collections import defaultdict
from TaggerClassifier import TaggerClassifier

class Application:
    """
    Master class of the Application
    """
    def __init__(self) -> None:
        self._connector = MySQL()       # MySQL connector to call methods of MySQL class
        self.assignment_to_users = defaultdict(dict)    # hashmap of {assignment_id: {user_id: list(answer_tags)}}
        self.tc = TaggerClassifier()                    # object of TaggerClassifier
        self.intervals = defaultdict(dict)              # (displaying purpose) hashmap of {assignment_id: {user_id: interval_logs_result}}
    
    def assignTaggerReliability(self):
        """
        Currently checks for fast tagging by calling interval logs method
        Assigns reliability per assignment per user
        """
        
        # Fetching the answer tags from the database
        tags = self._connector.getAnswerTags()
        
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
        for assignment_id, users in self.intervals.items():
            for user in users:
                print(assignment_id, user, self.intervals[assignment_id][user])
        

app = Application()
app.checkFastTagging()
        
    
    