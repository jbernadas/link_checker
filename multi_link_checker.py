#!/usr/bin/python3

## Note: Before running this script, make sure
## the site_report/example directory is populated with
## 'example-urls.txt' files, because this script reads
## off of it. You can populate the site_report/example
## directory by running the multi_site_report.py script.

import os
import time

targetnames = []

os.chdir('./site_report')
for (root, dirs, files) in os.walk('.'):
  for name in files:
    if '-urls.txt' in name:
      name_no_extension = name.split('-urls.txt')[0]
      targetnames.append(name_no_extension)

for targetname in targetnames:
  executeOrder67 = "python3 link_checker.py -r 0.8 {}".format(targetname)
  # os.system(executeOrder67)
  print(executeOrder67)
  time.sleep(1)
