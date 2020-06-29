from owlready2 import *
import datetime
import pandas as pd
from openpyxl import load_workbook
import rdflib

ns = "https://poneyponeymastersaga/myontology#"
# default_world.set_backend(filename="file_back3.sqlite3", exclusive=False)
# On crée une nouvelle ontologie
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

        def asignNewSymptoms(self, symps):
            self.hasSymptom = []
            self.asignSymptoms(symps)

    # class location(Thing):
    #     pass

    class location(Thing):
        pass

    class wilaya(location):
        pass

    class wilayaName(DataProperty, FunctionalProperty):
        domain = [wilaya]
        range = [str]

    class containPatient(location >> patient):
        pass

    class inLocation(patient >> location):
        inverse_property = containPatient

    class dayra(DataProperty, FunctionalProperty):
        domain = [patient]
        range = [str]

    class age(DataProperty, FunctionalProperty):
        domain = [patient]
        range = [int]

    class hasSymptom(ObjectProperty):
        domain = [patient]
        range = [symptoms]

    class chronicDesease(Thing):
        pass

    class hasChronicDesease(ObjectProperty):
        domain = [patient]
        range = [chronicDesease]

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

    class hasPatient(ObjectProperty, FunctionalProperty):
        domain = [consultation]
        range = [patient]

    class symptomsPresented(ObjectProperty):
        domain = [consultation]
        range = [symptoms]

    class output(DataProperty, FunctionalProperty):
        domain = [consultation]
        range = [str]

    class hadConsultation(ObjectProperty, FunctionalProperty):
        domain = [patient]
        range = [consultation]
        inverse_property = hasPatient
