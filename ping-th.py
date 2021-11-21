#!/usr/bin/env python

# ping a list of host with threads for increase speed
# use standard linux /bin/ping utility
# usage: $ python ping-th.py -f list-ips.csv

# based on https://gist.github.com/sourceperl/10288663

from threading import Thread
import subprocess
try:
    import queue
except ImportError:
    import Queue as queue
import re


import argparse
from csv import reader

__version__ = "0.0.1"


def parse_args():
  parser = argparse.ArgumentParser(description="Ping a list of devices")
  parser.add_argument("-f","--file", help="File with list of devices to ping")
  parser.add_argument(
    "-v",
    "--version",
    action="version",
    version="%(prog)s (version {})".format(__version__),
  )
  args = parser.parse_args()
  return args



# some global vars
num_threads = 15
ips_q = queue.Queue()
out_q = queue.Queue()


args = parse_args()

ips = []
reached = []
no_reached = []


# open file in read mode
with open(args.file, 'r') as read_obj:
  # pass the file oject to reader() to get the reader object
  csv_reader = reader(read_obj)
  # iterate over each row in the csv using reader
  for row in csv_reader:
  # row is a list that represents a row in csv. Just want first element
    ips.append(row[0])


# thread code : wraps system ping command
def thread_pinger(i, q):
  """Pings hosts in queue"""
  while True:
    # get an IP item form queue
    ip = q.get()
    # ping it
    args=['/bin/ping', '-c', '1', '-W', '1', str(ip)]
    p_ping = subprocess.Popen(args,
                              shell=False,
                              stdout=subprocess.PIPE)
    # save ping stdout
    p_ping_out = str(p_ping.communicate()[0])

    if (p_ping.wait() == 0):
      # rtt min/avg/max/mdev = 22.293/22.293/22.293/0.000 ms
      search = re.search(r'rtt min/avg/max/mdev = (.*)/(.*)/(.*)/(.*) ms',
                         p_ping_out, re.M|re.I)
      ping_rtt = search.group(2)
      out_q.put("OK," + str(ip) + ",rtt= "+ ping_rtt)
    else:
      out_q.put("FAIL," + str(ip))

    # update queue : this ip is processed 
    q.task_done()

# start the thread pool
for i in range(num_threads):
  worker = Thread(target=thread_pinger, args=(i, ips_q))
  worker.setDaemon(True)
  worker.start()

# fill queue
for ip in ips:
  ips_q.put(ip)

# wait until worker threads are done to exit    
ips_q.join()

# print result
while True:
  try:
    msg = out_q.get_nowait()
  except queue.Empty:
    break
  msg_list = msg.split(",")
  if msg_list[0] == "OK":
    reached.append(msg_list[1])
  else:
    no_reached.append(msg_list[1])
  print(msg)

print('')
print("#######################################")
print('')
print("Number of NO-reachable devices is: %s" % len(no_reached))
for i in no_reached:
  print(i)
print('')
print(','.join(no_reached))
print('')
print("#######################################")
print('')
print("Number of reachable devices is: %s" % len(reached))
for i in reached:
  print(i)
print('')
print(','.join(reached))
