#!/usr/bin/env python3

import argparse
import csv
import pandas

# TO-DO List
# - make no case sensitive the ports
# - pure python3?

__version__ = "0.0.1"


def parse_args():
  parser = argparse.ArgumentParser(description="Find peer from flapping link")
  parser.add_argument("-f","--file", help="File with flapping links: device,EthernetX/Y")
  parser.add_argument(
    "-v",
    "--version",
    action="version",
    version="%(prog)s (version {})".format(__version__),
  )
  args = parser.parse_args()
  return args

args = parse_args()

patching_file = "patching-file.csv"

# open patching plan
df1 = pandas.read_csv(patching_file, sep='\s*[,]', engine='python')
# this is the format of the patching plan
# Site, Source Device, Source Interface, Destination Device, Destination Interface, Media
# A,SW1,Ethernet1/1,SW2,Ethernet1/1,SMF

# create dataframe with only the specific columns to be able to make queries later on
df2 = pandas.DataFrame(df1,columns = ['Source Device','Source Interface','Destination Device','Destination Interface'])

print('\nResult:')

# open file in read mode for flapping links you want to find peer
with open(args.file, 'r') as read_obj:
    # pass te file object to reader() to get the reader object
    csv_reader = csv.reader(read_obj)
    # iterate over each row in the csv
    for row in csv_reader:
        a_device = row[0]
        a_port = row[1]
        # the link that is flapping can be a source or destination in the patching file so we make the query based on both options
        rslt_df = df2[((df2['Source Device'] == a_device.upper()) & (df2['Source Interface'] == a_port)) | ((df2['Destination Device'] == a_device.upper()) & (df2['Destination Interface'] == a_port)) ]
        # transform the Series (type used insde the datafram) to a list so we can take the first element (and should be the only one)
        df_a_device = rslt_df['Source Device'].tolist()[0]
        df_a_port = rslt_df['Source Interface'].tolist()[0]
        df_b_device = rslt_df['Destination Device'].tolist()[0]
        df_b_port = rslt_df['Destination Interface'].tolist()[0]
        print(df_a_device,df_a_port,df_b_device,df_b_port)

print()
