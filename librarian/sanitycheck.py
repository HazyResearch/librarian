#!/usr/bin/env python
"""sanitycheck.py Version 0.01

The sanitycheck tool is like 'lint' for data releases.  It examines
a data file (or directory) that you want to release.  It checks for
common errors and gives some summary statistics.  That's it!

The main goal with this tool is to catch common dumb mistakes before
they get shipped to a data consumer.  These common dumb mistakes are,
uh, common.  Incredibly common.  Better to catch them before anyone
sees them.

This is, obviously, a best-effort system.  The tool does what it can,
but no guarantees.  It only catches dumb mistakes, not clever mistakes.
"""

import argparse, json, os.path, hashlib, random, time, sys, shutil

#
# genStats() will create statistics about the TSV file
#
def genStats(fname, maxRows):
  """Examine a single file and return stats package"""
  MaxFieldLengths = 256
  MaxFieldValues = 256

  maxArity = 0
  arityHistogram = {}
  fieldLenHistograms = {}
  fieldTypeHistograms = {}
  fieldValueHistograms = {}
  
  with open(fname) as f:
    numRows = 0
    for r in f:
      if maxRows >= 0 and numRows >= maxRows:
        break
      numRows += 1      
      # Generate histogram of column arities
      parts = map(lambda x: x.strip(), r.split("\t"))
      arityHistogram[len(parts)] = arityHistogram.get(len(parts), 0) + 1

      maxArity = max(maxArity, len(parts))

      # Histogram of field lengths, types, and values, per column
      for i in range(0, len(parts)):
        fieldTypeLabel = "string"
        try:
          val = int(parts[i])
          fieldTypeLabel = "int"
        except Exception as exc:
          try:
            val = float(parts[i])
            fieldTypeLabel = "float"
          except Exception as exc2:
            pass

        fieldTypeHistogram = fieldTypeHistograms.setdefault(i, dict())
        fieldTypeHistogram[fieldTypeLabel] = fieldTypeHistogram.get(fieldTypeLabel, 0) + 1

        fieldLenHistogram = fieldLenHistograms.setdefault(i, dict())
        if len(fieldLenHistogram) < MaxFieldLengths:
          fieldLenHistogram[len(parts[i])] = fieldLenHistogram.get(len(parts[i]), 0) + 1

        fieldValueHistogram = fieldValueHistograms.setdefault(i, dict())
        if len(fieldValueHistogram) < MaxFieldValues:
          fieldValueHistogram[parts[i]] = fieldValueHistogram.get(parts[i], 0) + 1

  return maxArity, numRows, arityHistogram, fieldLenHistograms, fieldTypeHistograms, fieldValueHistograms
      

#
# String representation of a histogram
#
def renderHistogram(histogram, title):
  """Create a string representation of a histogram (stored in a hashtable)"""
  MaxStars = 50
  totalCount = 0
  for k, v in histogram.iteritems():
    totalCount += v

  countedPairs = []
  for k, v in histogram.iteritems():
    countedPairs.append((v, k))
  countedPairs.sort(reverse=True)

  totalSoFar = 0
  resultStr = title + "\n------------------------------------------------------------\n"
  for cp in countedPairs[0:20]:
    freq = cp[0]
    v = cp[1]    
    normFreq = freq / float(totalCount)

    if normFreq < 0.01:
      break
    
    totalSoFar += normFreq
    starCount = int(round(normFreq * MaxStars))
    stars = "*" * starCount
    resultStr += str(v) + "\t" + stars + "(" + str(normFreq) + ")\n"

  if totalSoFar < 1:
    missingFraction = 1-totalSoFar
    starCount = int(round(missingFraction * MaxStars))
    stars = "*" * starCount
    resultStr += "<Other>" + "\t" + stars + "(" + str(missingFraction) + ")\n"
  return resultStr
  

#
# This function applies rules of thumb to warn the user about suspicious
# things in the data
#
def examineFile(fname, printStats, maxRows):
  maxArity, numRows, arityHistogram, fieldLenHistograms, fieldTypeHistograms, fieldValueHistograms = genStats(fname, maxRows)

  numWarnings = 0

  # If the arity is not identical for all rows, warn user
  if len(arityHistogram) != 1:
    numWarnings += 1
    print "Warning: not all rows have identical # of columns"
    print renderHistogram(arityHistogram, "Tuple arity")
    print

  # If a single column mixes strings and numbers, warn the user
  for i in range(0, maxArity):
    fieldTypeHistogram = fieldTypeHistograms[i]
    if fieldTypeHistogram.get("string", 0) > 0 and (fieldTypeHistogram.get("int", 0) > 0 or fieldTypeHistogram.get("float", 0) > 0):
      numWarnings += 1
      print "Warning: column", i, "mixes strings and numerical quantities (#strs=" + str(fieldTypeHistogram.get("string", 0)) + ", #int=" + str(fieldTypeHistogram.get("int", 0)) + ", #float=" + str(fieldTypeHistogram.get("float", 0)) + ")"
      if printStats:
        print renderHistogram(fieldTypeHistogram, "Field Type Histogram for Column " + str(i))
        print

  # Commodity statistics
  if printStats:
    print "Number of rows:", numRows
    print "Maximum tuple arity:", maxArity
    print
    print "***********************"
    print "FIELD VALUE ANALYSIS"
    print "***********************"
    print
    for i in range(0, maxArity):
      fieldValueHistogram = fieldValueHistograms[i]
      print renderHistogram(fieldValueHistogram, "Field Value Histogram for Column " + str(i))
      print

    print
    print "***********************"
    print "FIELD LENGTH ANALYSIS"
    print "***********************"
    print
    for i in range(0, maxArity):
      fieldTypeHistogram = fieldTypeHistograms[i]
      if fieldTypeHistogram.get("string", 0) > 0:
        fieldLenHistogram = fieldLenHistograms[i]
        print renderHistogram(fieldLenHistogram, "Field Length Histogram for String Column " + str(i))
        print
      else:
        print "Column", i, "is not a String type"
        print

  print "Found", numWarnings, "warnings for file", os.path.abspath(fname)

#
# examine a file or a directory
#
def examine(fname, printStats=False, maxRows=500 * 1000):
  if os.path.isfile(fname):
    examineFile(fname, printStats, maxRows)
  else:
    for x in os.listdir(fname):
      examine(os.path.join(fname, x), printStats=printStats, maxRows=maxRows)

#
# main()
#
if __name__ == "__main__":
  usage = "usage: %prog [options]"
  parser = argparse.ArgumentParser(description="sanitycheck prevents MADNESS")

  parser.add_argument("--examine", nargs=1, metavar=("inputfile"), help="Examine an input file or directory")
  parser.add_argument("--stats", action="store_true", default=False, help="Print extra diagnostic information?")
  parser.add_argument("--maxrows", nargs=1, metavar=("maxrows"), help="Maximum # of rows to examine")
  parser.add_argument("--version", action="version", version="%(prog)s 0.1")

  args = parser.parse_args()
  maxrows = 20000
  try:
    if args.maxrows:
      maxrows = int(args.maxrows[0])
        
    if args.examine:
      examine(args.examine[0], printStats=args.stats, maxRows=maxrows)
    else:
      parser.print_help()
  except Exception as ex:
    print ex
  
