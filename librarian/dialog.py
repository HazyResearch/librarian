#!/usr/bin/env python
import sys

#
# q() is a helper function to make it easy to ask the user questions
# on the command-line
#
def q(questionText, qtype=None, args=None):
  """Ask the user a command-line question.  Return when there's a question that agrees with the type"""

  if qtype == "desc":
    answer = ""
    while len(answer.strip()) == 0:
      sys.stdout.write(questionText + "\n")
      sys.stdout.write("> ")        
      answer = sys.stdin.readline()
    return answer
  elif qtype == "yn":
    answer = ""
    while answer.strip().lower() not in ["y", "n", "yes", "no"]:
      sys.stdout.write(questionText + " [y/n] ")
      answer = sys.stdin.readline()

    if answer.strip().lower() in ["y", "yes"]:
      return True
    else:
      return False
  elif qtype == "multi":
    if args is None:
      raise Exception("No options provided to 'multi' question")
    answer = ""
    maxVal = len(args)+1

    while answer.strip() not in map(lambda x: str(x), range(1, maxVal)):
      sys.stdout.write(questionText + "\n")
      for idx, elt in enumerate(args):
        print "[" + str(idx) + "]  " + str(elt)

      sys.stdout.write("> ")  
      answer = sys.stdin.readline()
    return int(answer.strip())
  else:
    raise Exception("Unrecognized question type")

