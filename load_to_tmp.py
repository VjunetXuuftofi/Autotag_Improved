import csv

reader = csv.reader(open("loans.csv"))
writer = csv.writer(open("/tmp/loans.csv", "w"))
next(reader)
for row in reader:
    writer.writerow(row)