import csv

csvpath = '../input/Border_Crossing_Entry_Data.csv' # small file 6 records
csvpath2 = '../input/Border_Crossing_Entry_Data2.csv' # large file 300k records

data = {}
data2 = {}

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
    for measure in set(dictionary[reportkeys[2]]):  # running average is to be calculated for unique measures
        firstoccurrence = 0 # this variable indicates the measure has not been found yet.
        idx = []
        for m in range(len(dictionary[reportkeys[2]])-1,-1,-1):  # this loop runs on a sorted dictionary from bottom to top to look for first occurrences of measure.
            if dictionary[reportkeys[2]][m] == measure and firstoccurrence == 0:
                firstoccurrence = 1 # once it is found it is toggled and the running average is zero
                dictionary[reportkeys[4]][m] = 0
                idx.append(m)
            elif dictionary[reportkeys[2]][m] == measure and firstoccurrence == 1:
                tobesummed = [dictionary[reportkeys[3]][i] for i in idx]
                movavg = sum(tobesummed)/len(tobesummed)
                idx.append(m)
                movavg = proper_round(movavg)
                dictionary[reportkeys[4]][m] = movavg
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
            temp[key].append(f2[reportkeys[x]][idx])
        temp[key] = sorted(temp[key],reverse=True)

    return temp

# data = readfile(csvpath, data) # reading small file

data = readfile(csvpath2, data) # reading large file

keys = ['Port Name','State','Port Code','Border','Date','Measure','Value'] # columns of data stored as keys in dictionary


# for data2 (large file)
# groupby_date = groupby_column(data2,keys[4]) # grouping on dates. getting data indices
# groupby_measure = groupby_column(data2,keys[5]) # grouping on measure. getting data indices
# groupby_border = groupby_column(data2,keys[3]) # grouping on border. getting data indices

# for data (small file)
groupby_date = groupby_column(data,keys[4])    # grouping on dates. getting data indices
groupby_measure = groupby_column(data,keys[5]) # grouping on measure. getting data indices
groupby_border = groupby_column(data,keys[3])  # grouping on border. getting data indices

# keys or columns of report.csv
reportkeys = ['Border','Date','Measure','Value','Average']

## Forming a dictionary to group and sort data based on date, measure and intersection. Calculating Value of a measure in a month on a particular border.
f2 = {}
for key in reportkeys:
    f2[key] = []

for date in sorted(groupby_date,reverse=True):
    for measure in sorted(groupby_measure):
        for border in sorted(groupby_border):
            # intersection gives us the list of indices that are common for a border,measure and date.
            intersection = list(set(groupby_measure[measure]) & set(groupby_date[date]) & set(groupby_border[border]))
#             print(intersection)
            if len(intersection) != 0:
#                 res = [int(data[keys[6]][i]) for i in intersection]   # for small file
                res = [int(data[keys[6]][i]) for i in intersection]   # for large file
#                 print(border,date,measure,sum(res))
                f2[reportkeys[0]].append(border)
                f2[reportkeys[1]].append(date)
                f2[reportkeys[2]].append(measure)
                f2[reportkeys[3]].append(sum(res))
                f2[reportkeys[4]].append(0)

f2 = compute_movavg(f2)

groupby_value = groupby_column(f2, reportkeys[3])   # grouping on values. getting data indices
groupby_average = groupby_column(f2, reportkeys[4])  # grouping on average. getting data indices
groupby_date = groupby_column(f2, reportkeys[1])   # grouping on dates. getting data indices
groupby_measure = groupby_column(f2, reportkeys[2])  # grouping on measure. getting data indices
groupby_border = groupby_column(f2, reportkeys[0])  # grouping on border. getting data indices

## Sequentually this is the order in which the sorting of the outut file needs to be. Date -> Value -> Measure -> Border
t1 = link_twocols(groupby_date,3) # linking date and value
t2 = link_twocols(groupby_value,2) # linking value and measure
t3 = link_twocols(groupby_measure,0) # linking measure and border


## Writing final output to csv

i = 0
j = 0
k = 0
l = 0
filename = '../output/report.csv'
# writing to csv file
with open(filename, 'w') as csvfile:
    # creating a csv writer object
    csvwriter = csv.writer(csvfile)
    # writing the fields
    csvwriter.writerow(reportkeys)
    for date in t1:
    #     print(date)
        i = 0
        while(i!=len(t1[date])):
            value = t1[date][i]
            i = i + 1
    #         print(value)
            j = 0
            while(j!=len(t2[value])):
                measure = t2[value][j]
                j = j + 1
    #             print(measure)
                k = 0
                while(k!=len(t3[measure])):
                    border = t3[measure][k]
                    intersection = list(set(groupby_measure[measure]) & set(groupby_date[date]) & set(groupby_border[border]) & set(groupby_value[value]))
                    if len(intersection)!=0:
                        index = intersection[0]
#                     print(border,date,measure,value,f2[reportkeys[4]][index])
                        row = [border,date,measure,value,f2[reportkeys[4]][index]]
                        csvwriter.writerow(row)
                    break
