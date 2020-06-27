from owlready2 import *
from ontology import onto, symptoms, ns, patient, consultation
import rdflib
import csv


def addPatient(givenName, familyName, gender, age, dayra, wilaya, symps):
    _patient = patient(givenName=givenName, familyName=familyName,
                       gender=gender, age=age, dayra=dayra, wilaya=wilaya)
    for symp in symps:
        symp = symp.lower()
        if (onto.search(iri="*" + symp.replace(' ', '_')) == []):
            S = symptoms()
            S.iri = ns + symp.replace(' ', '_')
            _patient.hasSymptom.append(S)
        else:
            _patient.hasSymptom.append(onto.search(
                iri="*" + symp.replace(' ', '_'))[0])
    return _patient


def getPatient(iri):
    return onto.search(iri=ns+iri)[0]


def getPatients():
    return onto.search(type=patient)


def addConsultation(_patient):
    d = datetime.datetime.now().date()
    _consultation = consultation(date=str(d))
    _consultation.hasPatient = _patient
    _patient.hadConsultation.append(_consultation)
    return _consultation


def dbCommit():
    onto.save(file="out.rdf", format="ntriples")
    graph = rdflib.Graph()
    graph.parse("out.rdf", format='turtle')
    graph.serialize('out_turtle.rdf', format='turtle')


def clearIndividualsByClass(classs):
    symps = onto.search(type=classs)
    for i in symps:
        destroy_entity(i)


def write(onto):
    with open('patinets.csv', mode='w') as employee_file:
        patientWriter = csv.writer(
            employee_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        patientWriter.writerow(
            ['Nom', 'Prenom', 'Sexe', 'age', 'dayra', 'wilaya', 'Symptoms'])
        patientList = onto.search(type=patient)
        for _patient in patientList:
            symptomsList = ""
            for L in _patient.hasSymptom:
                symptomsList += "." + \
                    L.iri.replace(
                        "https://poneyponeymastersaga/myontology#", "")
            patientWriter.writerow([_patient.familyName, _patient.givenName, _patient.gender,
                                    _patient.age, _patient.dayra, _patient.wilaya, symptomsList])


# request = """
# prefix ns1: <https://poneyponeymastersaga/myontology#>
# prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# prefix xsd: <http://www.w3.org/2001/XMLSchema#>
# SELECT ?sn
# WHERE{
#     ?s rdf:type ns1:symptoms .
#     ?s ns1:sympName ?sn
#     FILTER regex(?sn, "fever")
# }
# """
# clearIndividualsByClass(symptoms)
# clearIndividualsByClass(patient)
# clearIndividualsByClass(consultation)
# dbCommit()
