from Models.AnswerTag import AnswerTag
import mysql.connector

class MySQL:
    """
    MySQL class is used to connect to MySQL database
    """
    def __init__(self) -> None:
        #connector to connect to  a live database
        self._connect()
    
    def _connect(self) -> None:
        self._mydb = mysql.connector.connect(host="localhost", user="root", password="ath@1234", database="expertiza")
        self._cursor = self._mydb.cursor()          #cursor to execute queries
        
    def getAnswerTags(self) -> list[object]:
        """
        Fetches the fields of Answer Tags and Assignment id by performing an inner join on answer_tags and tag_prompt_deployments
        Returns:
            list[object]: list of Answer Tags
        """
        tags = []
        
        #join query
        self._cursor.execute("SELECT a.id, t.assignment_id, a.answer_id, a.tag_prompt_deployment_id, a.user_id, a.value, a.created_at, a.updated_at FROM answer_tags a inner join tag_prompt_deployments t on a.tag_prompt_deployment_id=t.id")
        result = self._cursor.fetchall()
        
        #creating answer tag objects and returning a list of the objects
        for id, assignment_id, answer_id, tag_prompt_deployment_id, user_id, value, created_at, updated_at in result:
            tags.append(AnswerTag(id, assignment_id, answer_id, tag_prompt_deployment_id, user_id, value, created_at, updated_at))
        return tags