class NotValidOperator(Exception):
    """Not valid operator"""

class NotValidFile(Exception):
    """Not valid file"""

class NotOneOperatorInFile(Exception):
    """Not one operator in file"""

class EmptyDirectory(Exception):
    """There are no files in the directory"""

class NotValidSIMActivity(Exception):
    """The last activity of the SIM card is recorded in an incorrect format"""
    