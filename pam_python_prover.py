#!/usr/bin/python
import urllib2
import json
from time import sleep

PROVER_BASE_URL="http://10.82.0.103:9000/"
PROVER_SECRET="secret"

def pam_sm_authenticate(pamh, flags, argv):
  try:
    #generate a new token
    try:
      new_token_req = urllib2.urlopen(PROVER_BASE_URL + "retrieve?secret=" + PROVER_SECRET)
    except:
      send(pamh, "The identity service is not currently able to authenticate your identity. (0)")
      return pamh.PAM_PERM_DENIED

    decoded = json.load(new_token_req)

    if "error" in decoded.keys():
      send(pamh, "The identity service is not currently able to authenticate your identity. (1)")
      return pamh.PAM_PERM_DENIED

    token = decoded['token']
    send(pamh, "Navigate to " + PROVER_BASE_URL + "prove?token=" + token + " to confirm your identity.\nPress enter in this session once authenticated.")

    authed = False
    counter = 0
    username = ""

    while(not authed and counter < 120):
      try:
        check_req = urllib2.urlopen(PROVER_BASE_URL + "get?token=" + token + "&secret=" + PROVER_SECRET)
        response = json.load(check_req)
        if (response["proved"]):
          authed = True
          username = response["user"]
      except:
        pass

      counter = counter + 1
      sleep(1)

    if (authed):
        if (pamh.user == username):
          send(pamh, "Successfully authenticated as " + username + "; press enter to continue")
          return pamh.PAM_SUCCESS
        else:
          send(pamh, "You requested an session under username " + pamh.user + ", but were proven as " + username + "; Permission denied.")
          return pamh.PAM_PERM_DENIED

    if (counter >= 120):
      send(pamh, "Timeout reached.  Please try again.")

    return pamh.PAM_PERM_DENIED
  except Exception as excep:
    print(excep)

def pam_sm_setcred(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_acct_mgmt(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_open_session(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_close_session(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def pam_sm_chauthtok(pamh, flags, argv):
  return pamh.PAM_SUCCESS

def send(pamh, msg):
    #msg = str(msg)
    #return pamh.conversation(pamh.Message(pamh.PAM_TEXT_INFO, msg))
    prompt(pamh, msg)

def prompt(pamh, msg):
  msg = str(msg)
  return pamh.conversation(pamh.Message(pamh.PAM_PROMPT_ECHO_ON, msg))