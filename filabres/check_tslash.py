def check_tslash(dir):
    """Auxiliary function to add trailing slash when not present"""
    if dir[-1] != '/':
        dir += '/'
    return dir