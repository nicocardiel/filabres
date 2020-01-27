import datetime


def str2datetime(string):
    output = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S')
    return output
