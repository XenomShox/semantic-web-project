from quering_onto import *

# with open('./csv/wilayas.csv') as csv_file:
#     csv_reader = csv.reader(csv_file, delimiter=',')
#     # print(csv_reader)
#     i = 0
#     for row in csv_reader:
#         if i == 0:
#             i += 1
#         else:
#             x = wilaya(wilayaName=str(i) + "- " + row[2])
#             i += 1


w = wilaya(wilayaName="alger")
p = patient(givenName="Abdelhak", familyName="Ihadjadene", wilaya=w)

print(w.containPatientWilaya)
print(p.wilaya)

dbCommit()
