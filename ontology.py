from owlready2 import *
import datetime
import pandas as pd
from openpyxl import load_workbook
import rdflib
import os
from os.path import isfile

ns = "https://poneyponeymastersaga/myontology#"

if not isfile('./out.rdf'):
    open('out.rdf', 'w')
if not isfile('./out_turtle.rdf'):
    open('out_turtle.rdf', 'w')


onto = get_ontology("out.rdf").load()

with onto:
    class person(Thing):
        pass

    class symptoms(Thing):
        pass

    class givenName(DataProperty, FunctionalProperty):
        domain = [person]
        range = [str]

    class familyName(DataProperty, FunctionalProperty):
        domain = [person]
        range = [str]

    class gender(DataProperty, FunctionalProperty):
        domain = [person]
        range = [str]

    class patient(person):
        def asignSymptoms(self, symps):
            for symp in symps:
                symp = symp.lower()
                if (onto.search(iri="*" + symp.replace(' ', '_')) == []):
                    S = symptoms()
                    S.iri = ns + symp.replace(' ', '_')
                    self.hasSymptom.append(S)
                else:
                    self.hasSymptom.append(onto.search(
                        iri="*" + symp.replace(' ', '_'))[0])

        def asignDiseases(self, _diseases):
            for disease in _diseases:
                disease = disease.lower()
                if (onto.search(iri="*" + disease.replace(' ', '_')) == []):
                    S = diseases()
                    S.iri = ns + disease.replace(' ', '_')
                    self.hasDisease.append(S)
                else:
                    self.hasDisease.append(onto.search(
                        iri="*" + disease.replace(' ', '_'))[0])

        def asignTraitments(self, _traitments):
            for traitment in _traitments:
                traitment = traitment.lower()
                if (onto.search(iri="*" + traitment.replace(' ', '_')) == []):
                    S = traitments()
                    S.iri = ns + traitment.replace(' ', '_')
                    self.hasTraitment.append(S)
                else:
                    self.hasTraitment.append(onto.search(
                        iri="*" + traitment.replace(' ', '_'))[0])

        def asignNewSymptoms(self, symps):
            self.hasSymptom = []
            self.asignSymptoms(symps)

        def asignNewDiseases(self, diseases):
            self.hasDisease = []
            self.asignDiseases(diseases)

        def asignNewTraitments(self, traitments):
            self.hasTraitment = []
            self.asignTraitments(traitments)

    class location(Thing):
        pass

    class wilaya(location):
        pass

    class wilayaName(DataProperty, FunctionalProperty):
        domain = [wilaya]
        range = [str]

    class containPatientWilaya(wilaya >> patient):
        pass

    class inWilaya(patient >> wilaya, FunctionalProperty):
        python_name = "wilaya"
        inverse_property = containPatientWilaya

    class dayra(location):
        pass

    class dayraName(dayra >> str, FunctionalProperty):
        pass

    class containPatientDayra(dayra >> patient):
        pass

    class inDayra(patient >> dayra, FunctionalProperty):
        python_name = "dayra"
        inverse_property = containPatientDayra

    # class hasIn(wilaya >> dayra):
    #     pass

    # class inPartOf(dayra >> wilaya, FunctionalProperty):
    #     inverse_proprety = hasIn

    class age(DataProperty, FunctionalProperty):
        domain = [patient]
        range = [int]

    class isSymptomOf(patient >> symptoms):
        pass

    class hasSymptom(ObjectProperty):
        domain = [patient]
        range = [symptoms]
        inverse_property = isSymptomOf

    class diseases(Thing):
        pass

    class isDiseaseOf(patient >> symptoms):
        pass

    class hasDisease(ObjectProperty):
        domain = [patient]
        range = [diseases]
        inverse_property = isDiseaseOf

    class traitments(Thing):
        pass

    class isTraitmentOf(patient >> symptoms):
        pass

    class hasTraitment(ObjectProperty):
        domain = [patient]
        range = [traitments]
        inverse_property = isTraitmentOf

    class consultation(Thing):
        def asignSymptoms(self, symps):
            for symp in symps:
                symp = symp.lower()
                if (onto.search(iri="*" + symp.replace(' ', '_')) == []):
                    S = symptoms()
                    S.iri = ns + symp.replace(' ', '_')
                    self.symptomsPresented.append(S)
                else:
                    self.symptomsPresented.append(onto.search(
                        iri="*" + symp.replace(' ', '_'))[0])

        def asignNewSymptoms(self, symps):
            self.symptomsPresented = []
            self.asignSymptoms(symps)

    class date(DataProperty, FunctionalProperty):
        domain = [consultation]
        range = [str]

    class symptomsPresented(ObjectProperty):
        domain = [consultation]
        range = [symptoms]

    class output(DataProperty, FunctionalProperty):
        domain = [consultation]
        range = [str]

    class hadConsultation(patient >> consultation):
        pass

    class hasPatient(consultation >> patient, FunctionalProperty):
        inverse_property = hadConsultation
