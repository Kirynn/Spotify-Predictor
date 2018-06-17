'''
A collection of utilties to make life easier.
'''
import pip
import json
from platform import system
from subprocess import Popen
from getpass import getuser
        

def isUser(user):

    return user == getuser()

def pipInstall(packageName):

    try: pip.main(['install', packageName])
    except: print('Something went wrong')

def prettyDict(d):
    
    return json.dumps(d, indent=2)

def wait():

    input('Press Any Key To Continue...')

def average(args):

    return sum(*args)/len(*args)
