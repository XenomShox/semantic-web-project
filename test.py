from quering_onto import *

wilayas = ["1 - ADRAR", "2 - CHLEF", "3 - LAGHOUAT", "4 - OUM BOUAGHI", "5 - BATNA", "6 - BEJAIA", "7 - BISKRA",
           "8 - BECHAR", "9 - BLIDA", "10 - BOUIRA", "11 - TAMANRASSET", "12 - TEBESSA", "13 - TLEMCEN",
           "14 - TIARET", "15 - TIZI OUZOU", "16 - ALGER", "17 - DJELFA", "18 - JIJEL", "19 - SETIF", "20 - SAIDA",
           "21 - SKIKDA", "22 - SIDI BEL ABBES", "23 - ANNABA", "24 - GUELMA", "25 - CONSTANTINE", "26 - MEDEA",
           "27 - MOSTAGANEM", "28 - M'SILA", "29 - MASCARA", "30 - OUARGLA", "31 - ORAN", "32 - EL BAYDH",
           "33 - ILLIZI", "34 - BORDJ BOU ARRERIDJ", "35 - BOUMERDES", "36 - EL TAREF", "37 - TINDOUF",
           "38 - TISSEMSILT", "39 - EL OUED", "40 - KHENCHLA", "41 - SOUK AHRASS", "42 - TIPAZA", "43 - MILA",
           "44 - AÏN DEFLA", "45 - NÂAMA", "46 - AÏN TEMOUCHENT", "47 - GHARDAÏA", "48 - RELIZANE",
           "49 - Bordj Badji Mokhtar", "50 - In Salah", "51 - Djanet", "52 - In Guezzem", "53 - El Mghaier", "54 - Touggourt",
           "55 - Béni Abbes", "56 - Timinoune", "57 - Ould Djelel", "58 - El Menia"]
for i in wilayas:
    newWilaya = wilaya(wilayaName=i)


print(onto.search(type=onto.wilaya))
# print(onto.search(type=onto.wilaya))