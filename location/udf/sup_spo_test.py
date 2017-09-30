import csv
with open('query_result-2.csv','rb') as csvin:
    res_reader = csv.DictReader(csvin,delimiter = ';')
    for row in res_reader:
        for k,v in row.iteritems():
            print k,v
        exit(0)
