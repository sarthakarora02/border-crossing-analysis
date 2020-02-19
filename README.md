# insight-borderanalysis

Using Dictionaries to store, group and link data and calculate the sum of the values of crossings of a particular measure during a month and across a particular border, and the running average of different measures over the course of months

## How to run
If in the src directory
 - python border_analysis.py ../input/Border_Crossing_Entry_Data.csv ../output/report.csv

./run.sh will has two iterations:
 - one over the small file (./input/Border_Crossing_Entry_Data.csv)
 - one over the large file (./input/Border_Crossing_Entry_Data2.csv) #currently this is commented out
