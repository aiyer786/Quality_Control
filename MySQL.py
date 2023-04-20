from Models.AnswerTag import AnswerTag
from Models.Answer import Answer
from Models.Assignment import Assignment
from Models.Team import Team
from Models.User import User
import mysql.connector

class MySQL:
    """
    MySQL class is used to connect to MySQL database
    """
    def __init__(self) -> None:
        #connector to connect to  a live database
        self._connect()
    
    def _connect(self) -> None:
        self._mydb = mysql.connector.connect(host="lin-res44.csc.ncsu.edu", user="tagging", password="expertizatagging", database="expertiza_production")
        #self._mydb = mysql.connector.connect(host="localhost", user="root", password="ath@1234", database="expertiza")
        self._cursor = self._mydb.cursor()          #cursor to execute queries
        
    def getAnswerTags(self) -> list[object]:
        """
        Fetches the fields of Answer Tags and Assignment id by performing an inner join on answer_tags and tag_prompt_deployments
        Returns:
            list[object]: list of Answer Tags
        """
        tags = []
        
        #join query
        self._cursor.execute("SELECT a.id, t.assignment_id, a.answer_id, a.tag_prompt_deployment_id, a.user_id, a.value, a.created_at, a.updated_at FROM answer_tags a inner join tag_prompt_deployments t on a.tag_prompt_deployment_id=t.id order by a.created_at desc")
        result = self._cursor.fetchall()
        
        #creating answer tag objects and returning a list of the objects
        for id, assignment_id, answer_id, tag_prompt_deployment_id, user_id, value, created_at, updated_at in result:
            tags.append(AnswerTag(id, assignment_id, answer_id, tag_prompt_deployment_id, user_id, value, created_at, updated_at))
        return tags
    
    def getUserTeams(self) -> dict:
        """
        Fetches the tags of all users pertaining to a team for all assignments
        Returns:
            dict: dictionary of the form -> {assignment_id: {teams_id: {user_id: {answer_id: {tag_prompt_id: tag}}}}}
        """
        assignment_to_teams = {}
        
        #join query
        self._cursor.execute('''select v1.id, v2.team_id, v1.answer_id, v1.tag_prompt_deployment_id, 
                             v1.user_id, v1.value, v1.tag_prompt_id, v1.assignment_id, v1.created_at, v1.updated_at 
                             from view1 v1 inner join view2 v2 on v1.user_id=v2.user_id and v1.assignment_id=v2.assignment_id;''')
        result = self._cursor.fetchall()
        
        #creating the dictionary
        for answer_tag_id, team_id, answer_id, tag_prompt_deployment_id, user_id, value, tag_prompt_id, assignment_id, created_at, updated_at in result:
            #creating answer tag
            tag = AnswerTag(answer_tag_id, assignment_id, answer_id, tag_prompt_deployment_id, user_id, value, created_at, updated_at, tag_prompt_id)
            if assignment_id in assignment_to_teams:
                if team_id in assignment_to_teams[assignment_id].teams:
                    if user_id in assignment_to_teams[assignment_id].teams[team_id].users:
                        if answer_id in assignment_to_teams[assignment_id].teams[team_id].users[user_id].answers:
                            #Answer is already present, add the tag_prompt_id with corresponding tag
                            assignment_to_teams[assignment_id].teams[team_id].users[user_id].answers[answer_id].tags[tag_prompt_id] = tag
                        else:
                            #Answer not present, create a new answer object
                            new_answer = Answer()
                            new_answer.tags = {tag_prompt_id: tag}
                            assignment_to_teams[assignment_id].teams[team_id].users[user_id].answers[answer_id] = new_answer
                    else:
                        #user not present, create a new user
                        new_answer = Answer()
                        new_answer.tags = {tag_prompt_id: tag}
                        
                        new_user = User()
                        new_user.answers = {answer_id: new_answer}
                        assignment_to_teams[assignment_id].teams[team_id].users[user_id] = new_user
                else:
                    #team not present, create a new team
                    new_answer = Answer()
                    new_answer.tags = {tag_prompt_id: tag}
                    
                    new_user = User()
                    new_user.answers = {answer_id: new_answer}
                    
                    new_team = Team()
                    new_team.users = {user_id: new_user}
                    
                    assignment_to_teams[assignment_id].teams[team_id] = new_team
            else:
                #assignmnet not present, create a new assignment
                new_answer = Answer()
                new_answer.tags = {tag_prompt_id: tag}
                
                new_user = User()
                new_user.answers = {answer_id: new_answer}
                
                new_team = Team()
                new_team.users = {user_id: new_user}
                
                new_assigment = Assignment()
                new_assigment.teams = {team_id: new_team}
                assignment_to_teams[assignment_id] = new_assigment
                            
        return assignment_to_teams
            
                
                