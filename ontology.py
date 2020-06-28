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

    class wilaya(DataProperty, FunctionalProperty):
        domain = [patient]
        range = [str]

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
        pass

    class date(DataProperty, FunctionalProperty):
        domain = [consultation]
        range = [str]

    class hasPatient(ObjectProperty, FunctionalProperty):
        domain = [consultation]
        range = [patient]

    class output(DataProperty, FunctionalProperty):
        domain = [consultation]
        range = [str]

    class hadConsultation(ObjectProperty):
        domain = [patient]
        range = [consultation]

# soreness = symptoms("soreness")
# soreThroat = symptoms("soreThroat")
# nasalCongestion = symptoms("nasalCongestion")
# runnyNose = symptoms("runnyNose")
# cough = symptoms("cough")
# dryCough = symptoms("dryCough")
# diarrhea = symptoms('diarrhea')
# fever = symptoms('fever')
# fatigue = symptoms('fatigue')
# pneumonia = symptoms('pneumonia')
# severePneumonia = symptoms('severePneumonia')
# SDRA = symptoms('SDRA')
# septicShock = symptoms('septicShock')
# sepsis = symptoms('sepsis')
