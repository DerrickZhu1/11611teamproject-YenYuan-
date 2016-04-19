'''
Created on Apr 8, 2016

@author: zhongzhu
'''
from datetime import datetime

# start immediately
start = datetime.now()

def timer_log(task=""):
    global start
    end = datetime.now()
    print("[Timer] " + task + ": " + str(end - start))
    start = datetime.now()

