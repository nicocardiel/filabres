def check_tslash(dumdir):
    """Auxiliary function to add trailing slash when not present"""
    if dumdir[-1] != '/':
        dumdir += '/'
    return dumdir