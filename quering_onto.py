from owlready2 import *
from ontology import onto, symptoms, diseases, ns, patient, consultation, wilaya, dayra
import rdflib
import csv


def addPatient(givenName, familyName, gender, age, dayra, wilaya, symps):
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


def write(patientList):  # give her the getpatients method
    with open('patinets.csv', mode='w') as csv_file:
        fieldnames = ['givenName', 'familyName', 'gender',
                      'wilaya', 'dayra', 'age', 'symptoms']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for _patient in patientList:
            writer.writerow(getPatientData(_patient))


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
        "wilaya": _patient.wilaya.wilayaName,
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
