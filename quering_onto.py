from owlready2 import *
from ontology import onto, symptoms, diseases, ns, patient, consultation, wilaya, dayra
import rdflib
import csv

# Une fonction qui permet de créer un individue patient


def addPatient(givenName, familyName, gender, age, wilaya, symps):
    w = find_v2(onto.wilaya, {
        "wilayaName": wilaya
    })[0]

    _patient = patient(givenName=givenName, familyName=familyName,
                       gender=gender, age=age, wilaya=w)
    _patient.asignSymptoms(symps)
    return _patient

# Fonction qui permet de créer un individue consultation


def addConsultation(_patient):
    d = datetime.datetime.now().date()
    _consultation = consultation(date=str(d))
    _consultation.hasPatient = _patient
    # _patient.hadConsultation.append(_consultation)
    return _consultation


# Fonction pour recuperer un patient a partir de son "name"
def getPatient(iri):
    return onto.search(iri=ns+iri)[0]

# Fonction pour recuperer tous les Patients


def getPatients():
    return onto.search(type=patient)

# Fonction pour recuperer toutes les Consultations


def getConsultations():
    return onto.search(type=consultation)

# Fonction qui permet de sauvgarder notre current Graph


def dbCommit():
    onto.save(file="out.owl", format="ntriples")
    graph = rdflib.Graph()
    graph.parse("out.owl", format='turtle')
    graph.serialize('out_turtle.rdf', format='turtle')

# fonction qui clear tous les individues d'une class donnée


def clearIndividualsByClass(classs):
    individuals = onto.search(type=classs)
    for individual in individuals:
        destroy_entity(individual)

# Helper function pour get tous les individues d'une class


def getIndividualsByClass(c):
    return onto.search(type=c)

# Helper function pour get un individue a partir de son iri


def getIndividualByURI(iri):
    return onto.search(iri="*" + iri)[0]


# Helper function qui permet de transformer une liste d'individues (symptomes, traitement, Maladies)
# en une liste de strings, pour afficher


def opToList(X):
    lis = []
    for L in X:
        lis.append(L.name)
    return lis

# Helper function qui prend une liste de consultations et retourne une liste
# de Dictionaire qui represente une consultation, aussi pour affichage


def getConsultationsData(csMap):
    consultationsList = []
    for cs in csMap:
        consultationsList.append(getConsultationData(cs))
    return consultationsList


# Helper function utilisé dans getConsultationsData
def getConsultationData(_consultation):
    consultationDic = {
        "patient": getPatientData(_consultation.hasPatient),
        "date": _consultation.date,
        "output": _consultation.output,
        "id": _consultation.name,
        "symptoms": opToList(_consultation.symptomsPresented)
    }
    return consultationDic


# Helper function qui prend une liste de patients et retourne une liste
# de Dictionaire qui represente un patient, aussi pour affichage
def getPatientsData(patients):
    patientsList = []
    for _patient in patients:
        patientsList.append(getPatientData(_patient))
    return patientsList

# Helper function utilisé dans getPatientsData


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


# Older version of find_v2
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

# Au debut on utiliser les fonction getIndividualByURI et getIndividualByClass
# On a ensuite pensé a une idée, pour éviter les requetes sparql
# Donc on a crée une fonction generique pour chercher des individues avec des contraintes
# par exmp: on veut chercher in individue dans la class patient, qui on pour givenName: 'Abdelhak'
# et pour familyName: 'Ihadjadene', donc on écrit find_v2(onto.patient, {'givenName': 'Abdelhak', 'familyName': 'Ihadjadene'})


def find_v2(_object, dic={}):
    objects = getIndividualsByClass(_object)
    L = []
    for o in objects:
        s = tuple([getattr(o, x) for x in dic])
        _s = tuple([dic[x] for x in dic])
        if s == _s:
            L.append(o)
    return L

# les 2 prochaines fonction sont des fonction d'enraichissement de notre ontology


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

# Les 2 prochaines fonction sont utilisé pour extraire un fichier CSV de nos patient et consultations


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
