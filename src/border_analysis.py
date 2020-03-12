import csv
import argparse
import json
import operator
from datetime import datetime

csvpath = '../input/Border_Crossing_Entry_Data.csv' # small file 6 records

data = {}

def readfile(csvpath, dictionary):
    ## Function to read csv from given path and store data columnwise in a dictionary.
    ## keys of dictionary are columns of data.
    ## Inputs:
    ## - csvpath - path to csv of data. Stored under input
    ## - dictionary - dictionary data structure to store data.
    ## Returns dictionary passed as input, with data stored in it

    with open(csvpath) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for i,row in enumerate(readCSV):
            if i == 0:
                cols = row
                for colname in row:
                    dictionary[colname] = []
            else:
                for j,value in enumerate(row):
                    dictionary[cols[j]].append(value)
    return dictionary

def groupby_column(dictionary, column):
    ## Function to group data based on a column
    ## keys of dictionary are columns of data.
    ## Inputs:
    ## - dictionary - dictionary data structure in which data is stored
    ## - column - the parameter over which the data is grouped
    ## returns a dictionary of the grouped data as keys and the values being the indices.
    temp = {}
    for index, key in enumerate(dictionary[column]):
        try:
            temp[key].append(index)
        except:
            temp[key] = [index]
    return temp

def proper_round(num):
    ## Function to properly round up or down Average values to nearest integer.
    ## Decimal value >= 5 are rounded up else rounded down
    ## Inputs:
    ## - num - number to be rounded
    ## returns num after appropriate rounding
#     print(num)
    temp = str(num)
    temp = temp.split('.')
    if int(temp[1]) >= 5:
        return int(temp[0])+1
    else:
        return int(temp[0])


def compute_movavg(dictionary):
    ## Function to compute running average of values in data
    ## Inputs:
    ## - dictionary - dictionary of data for which running average needs to be calculated.
    ## returns dictionary with running average values
    # print(json.dumps(dictionary,indent=4))
    movavg = {}
    for index,pair in reversed(list(enumerate(zip(dictionary[reportkeys[2]],dictionary[reportkeys[0]])))):
        # print(index,pair)
        try:
            movavg[pair].append(index)
        except:
            movavg[pair] = [index]

    # print(movavg)
    # print(dictionary[reportkeys[3]])

    for pair in movavg:
        # print(pair)
        for i,idx in enumerate(movavg[pair]):
            # print(i,idx)
            if i == 0:
                dictionary[reportkeys[4]][idx] = 0
            else:
                # print(movavg[pair][:i])
                tobesummed = [dictionary[reportkeys[3]][j] for j in movavg[pair][:i]]
                # print(tobesummed)
                runavg = sum(tobesummed)/len(tobesummed)
                runavg = proper_round(runavg)
                # print(idx,runavg)
                dictionary[reportkeys[4]][idx] = runavg
    # print(dictionary[reportkeys[4]])

    return dictionary


def link_twocols(groupby, x):
    ## Function to link two columns as a dictionary
    ## Inputs:
    ## - groupby - one of the groupby variables for linking to x
    ## - x - index of the reportkeys to link with groupby variable
    ## returns dictionary with pairs of columns linked as key value
    temp = {}
    for key in groupby:
        temp[key] = []
        for idx in groupby[key]:
            temp[key].append(final[reportkeys[x]][idx])
        temp[key] = sorted(temp[key],reverse=True)

    return temp

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("csvpath")
    parser.add_argument("outputpath")
    csvpath = parser.parse_args().csvpath
    outputpath = parser.parse_args().outputpath

    data = readfile(csvpath, data) # reading large file

    keys = ['Port Name','State','Port Code','Border','Date','Measure','Value'] # columns of data stored as keys in dictionary

    groupby_date = groupby_column(data,keys[4])    # grouping on dates. getting data indices
    groupby_measure = groupby_column(data,keys[5]) # grouping on measure. getting data indices
    groupby_border = groupby_column(data,keys[3])  # grouping on border. getting data indices

    # keys or columns of report.csv
    reportkeys = ['Border','Date','Measure','Value','Average']

    ## Forming a final dictionary for sorted data with value and average calculated
    final = {}
    for key in reportkeys:
        final[key] = []

    # Batchwise data being added to final based on Date as formatted and sorted with datetime
    for date in sorted(groupby_date,reverse=True, key=lambda x: datetime.strptime(x, '%m/%d/%Y %I:%M:%S %p')):
        # print(date)
        date_dictionary = {}
        # To group Measure and Border for corresponding date
        for index in groupby_date[date]:
            measure_border_pair = (data[reportkeys[2]][index],data[reportkeys[0]][index])
            # print(measure_border_pair)
            try:
                date_dictionary[measure_border_pair].append(index)
            except:
                date_dictionary[measure_border_pair] = [index]

        # print(date_dictionary)

        ## Forming a final dictionary for data with value calculated for particular date
        batch_final = {}
        for key in reportkeys:
            batch_final[key] = []

        for pair in date_dictionary:
            tobesummed = [int(data[reportkeys[3]][j]) for j in date_dictionary[pair]]
            # print(pair)
            # print(tobesummed)
            batch_final[reportkeys[0]].append(pair[1])           # appending border
            batch_final[reportkeys[1]].append(date)              # appending date
            batch_final[reportkeys[2]].append(pair[0])           # appending measure
            batch_final[reportkeys[3]].append(sum(tobesummed))   # appending value
            batch_final[reportkeys[4]].append(0)                 # appending averge as 0 for now

        # Sorting the batch date data for Value and Measure.
        batch_final = sorted(zip(batch_final[reportkeys[0]],batch_final[reportkeys[1]],batch_final[reportkeys[2]],batch_final[reportkeys[3]],batch_final[reportkeys[4]]),key=operator.itemgetter(2))
        batch_final = sorted(batch_final,key=operator.itemgetter(3),reverse=True)

        # Adding the date batch final data to final dictionary
        for row in batch_final:
            final[reportkeys[0]].append(row[0])
            final[reportkeys[1]].append(row[1])
            final[reportkeys[2]].append(row[2])
            final[reportkeys[3]].append(row[3])
            final[reportkeys[4]].append(row[4])

    # print(json.dumps(final,indent=4))

    # Compute moving average for all final data
    final = compute_movavg(final)
    # print(json.dumps(final,indent=4))

    ## Writing final output to csv
    filename = outputpath
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        # writing the fields
        csvwriter.writerow(reportkeys)
        csvwriter.writerows(zip(final[reportkeys[0]],final[reportkeys[1]],final[reportkeys[2]],final[reportkeys[3]],final[reportkeys[4]]))
