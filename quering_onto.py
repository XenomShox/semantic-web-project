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
    onto.save(file="out.rdf", format="ntriples")
    graph = rdflib.Graph()
    graph.parse("out.rdf", format='turtle')
    graph.serialize('out_turtle.rdf', format='turtle')


def clearIndividualsByClass(classs):
    symps = onto.search(type=classs)
    for i in symps:
        destroy_entity(i)


def write(patientList):  # give her the getpatients method
    with open('patinets.csv', mode='w') as csv_file:
        fieldnames = ['givenName', 'familyName', 'gender',
                      'wilaya', 'dayra', 'age', 'symptoms']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for _patient in patientList:
            writer.writerow(getPatientData(_patient))

# you give her the getConsultations method as an argument returns a list of dictionaries.


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


if len(find_v2(onto.wilaya)) == 0:
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
