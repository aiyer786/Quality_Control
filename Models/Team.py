class Team:
    # This class represents a Team object that can be used to store information about a group of users.
    def __init__(self) -> None:
        self.users = {}
        # The 'users' dictionary stores key-value pairs where the keys are user IDs and the values are user data.