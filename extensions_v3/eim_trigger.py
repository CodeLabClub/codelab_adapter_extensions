import time

def trigger():
    '''
    Trigger a message
    '''
    timestamp = time.time()
    time.sleep(1)
    return timestamp
