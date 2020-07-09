from owlready2 import *
from ontology import onto, symptoms, diseases, ns, patient, consultation, wilaya, dayra
import rdflib
import csv


def addPatient(givenName, familyName, gender, age, wilaya, symps):
    w = find_v2(onto.wilaya, {
        "wilayaName": wilaya
    })[0]

    _patient = patient(givenName=givenName, familyName=familyName,
                       gender=gender, age=age, wilaya=w)
    _patient.asignSymptoms(symps)
    return _patient


def getPatient(iri):
    return onto.search(iri=ns+iri)[0]


def getPatients():
    return onto.search(type=patient)


def addConsultation(_patient):
    d = datetime.datetime.now().date()
    _consultation = consultation(date=str(d))
    _consultation.hasPatient = _patient
    # _patient.hadConsultation.append(_consultation)
    return _consultation


def getConsultations():
    return onto.search(type=consultation)


def dbCommit():
    onto.save(file="out.owl", format="ntriples")
    graph = rdflib.Graph()
    graph.parse("out.owl", format='turtle')
    graph.serialize('out_turtle.rdf', format='turtle')


def clearIndividualsByClass(classs):
    individuals = onto.search(type=classs)
    for individual in individuals:
        destroy_entity(individual)


# def write(patientList):  # give her the getpatients method
#     with open('patinets.csv', mode='w') as csv_file:
#         fieldnames = ['givenName', 'familyName', 'gender',
#                       'wilaya', 'dayra', 'age', 'symptoms']
#         writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
#         writer.writeheader()
#         for _patient in patientList:
#             writer.writerow(getPatientData(_patient))


def opToList(X):
    lis = []
    for L in X:
        lis.append(L.name)
    return lis


def getConsultationsData(csMap):
    consultationsList = []
    for cs in csMap:
        consultationsList.append(getConsultationData(cs))
    return consultationsList


# you give her a consultation and it returns it's data in a dic
def getConsultationData(_consultation):
    consultationDic = {
        "patient": getPatientData(_consultation.hasPatient),
        "date": _consultation.date,
        "output": _consultation.output,
        "id": _consultation.name,
        "symptoms": opToList(_consultation.symptomsPresented)
    }
    return consultationDic


def getPatientData(_patient):  # you give her a patient and it returns it's data in a dic
    patientDic = {
        "givenName": _patient.givenName,
        "familyName": _patient.familyName,
        "gender": _patient.gender,
        "wilaya": _patient.wilaya.wilayaName.split(' ')[-1],
        # "dayra": _patient.dayra.dayraName,
        "age": _patient.age,
        "symptoms": opToList(_patient.hasSymptom),
        "chronic_diseases": opToList(_patient.hasDisease),
        "traitments": opToList(_patient.hasTraitment)
    }
    return patientDic


# you give her the getpatients method as an argument sand it returns a list of dictionaries
def getPatientsData(patients):
    patientsList = []
    for _patient in patients:
        patientsList.append(getPatientData(_patient))
    return patientsList


def getSymptomData(_symptom):
    symptomDic = {
        "name": _symptom.name,
        "N": len(_symptom.isSymptomOf),
        "patients": opToList(_symptom.isSymptomOf)
    }
    return symptomDic


def getSymptomsData(symptoms):
    symptomsList = []
    for _symptom in symptoms:
        symptomsList.append(getPatientData(_symptom))
    return symptomsList


def getIndividualsByClass(c):
    return onto.search(type=c)


def getIndividualByURI(iri):
    return onto.search(iri="*" + iri)[0]


def find_v1(clas, attributes):
    individuals = getIndividualsByClass(clas)
    lis = []
    for individual in individuals:
        checked = True
        for key, value in attributes.items():
            if not (getattr(individual, key) == value):
                checked = False
                break
        if checked:
            lis.append(individual)
    return lis


def find_v2(_object, dic={}):
    objects = getIndividualsByClass(_object)
    L = []
    for o in objects:
        s = tuple([getattr(o, x) for x in dic])
        _s = tuple([dic[x] for x in dic])
        if s == _s:
            L.append(o)
    return L


def enrichSymptomsDiseases():
    with open('./csv/dataset.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line = 0
        dataset = {}
        for row in csv_reader:
            if line == 0:
                line += 1
            else:
                disease = row[0].lower().strip().replace(' ', '_')
                dataset[disease] = dataset.get(disease, [])
                for i in range(1, len(row)):
                    if not row[i] == '':
                        symptom = row[i].lower().strip().replace(
                            ' ', '_').replace('__', '_')
                        if symptom not in dataset[disease]:
                            dataset[disease].append(symptom)

    for key, value in dataset.items():
        if len(find_v2(onto.diseases, {"name": key})) == 0:
            d = diseases(key)
        for symptom in value:
            if len(find_v2(onto.symptoms, {"name": symptom})) == 0:
                s = symptoms(symptom)

    dbCommit()


def enrichWilaya():
    with open('./csv/wilayas.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        # print(csv_reader)
        i = 0
        for row in csv_reader:
            if i == 0:
                i += 1
            else:
                x = wilaya(wilayaName=str(i) + "- " + row[2])
                i += 1
    dbCommit()


if len(find_v2(onto.wilaya)) == 0:
    enrichWilaya()

if len(find_v2(onto.diseases)) == 0 and len(find_v2(onto.symptoms)) == 0:
    enrichSymptomsDiseases()


def CSV_patients():
    with open('patients.csv', 'w', newline='') as csv_file:
        fieldnames = ['id', "Nom", 'Prenom', 'Sexe', 'Age',
                      'Wilaya', 'Symptoms', 'Maladies', 'Traitement']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        patients = getPatientsData(find_v2(onto.patient))
        id = 1
        for patient in patients:
            objToWrite = {
                'id': str(id),
                'Nom': patient['familyName'],
                'Prenom': patient['givenName'],
                'Age': patient['age'],
                'Sexe': patient['gender'],
                'Wilaya': patient['wilaya'],
                'Symptoms': " - ".join(patient['symptoms']).replace('_', ' '),
                'Maladies': " - ".join(patient['chronic_diseases']).replace('_', ' '),
                'Traitement': " - ".join(patient['traitments']).replace('_', ' ')
            }
            writer.writerow(objToWrite)
            id += 1


def CSV_consultations():
    # consultationDic = {
    #     "patient": getPatientData(_consultation.hasPatient),
    #     "date": _consultation.date,
    #     "output": _consultation.output,
    #     "id": _consultation.name,
    #     "symptoms": opToList(_consultation.symptomsPresented)
    # }
    with open('consultations.csv', 'w', newline='') as csv_file:
        fieldnames = ['id', "Nom Complet",
                      'Symptoms pendent consultation', 'Date', 'Verdict']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        consultations = getConsultationsData(find_v2(onto.consultation))
        id = 1
        for consultation in consultations:
            objToWrite = {
                'id': str(id),
                'Nom Complet': consultation['patient']['givenName'] + " " + consultation['patient']['familyName'],
                'Symptoms pendent consultation': " - ".join(consultation['symptoms']).replace('_', ' '),
                'Date': consultation['date'],
                'Verdict': consultation['output']
            }

            if objToWrite['Verdict']:
                objToWrite['Verdict'].replace('\n', ' ')
            writer.writerow(objToWrite)
            id += 1
