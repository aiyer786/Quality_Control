class Assignment:
    #This class represents an Assignment object that can be used to store information about teams and their assignments.
    def __init__(self) -> None:
        self.teams = {}
        #The 'teams' dictionary is used to store key-value pairs where the keys are team names and the values are lists of assignments associated with that team.