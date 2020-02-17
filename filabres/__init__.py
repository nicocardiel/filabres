from .version import version
__version__ = version

# requirement operators (using the logical operators syntax from Fortran77)
REQ_OPERATORS = {
    '.NE.': '!=',
    '.GT.': '>',
    '.GE.': '>=',
    '.LT.': '<',
    '.LE.': '<='
}

LISTDIR = './lists/'
