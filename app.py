from flask import Flask, render_template, request, redirect
from ontology import onto, consultation
from quering_onto import addPatient, addConsultation, symptomsToList, dbCommit, getPatient, getConsultationsData, getConsultationData, getIndividualByURI

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/consultations')
def consultations():
    csMap = onto.search(iri="*consultation*")
    csMap = csMap[1:]
    consultations = getConsultationsData(csMap)
    return render_template('consultations.html', consultations=consultations)


@app.route('/consultation/<id>', methods=['GET', 'POST'])
def consultation(id):
    consultation = getIndividualByURI(id)
    consultationData = getConsultationData(consultation)
    if request.method == 'POST':
        # print(request.form['output'].split('\n'))
        consultation.output = request.form['output'].replace('\r', '')
        dbCommit()
        return redirect("/consultation/" + id)
    else:
        return render_template('consultation.html', consultation=consultationData)


@app.route('/consultation/create', methods=['GET', 'POST'])
def createConsultation():
    if request.method == 'POST':
        givenName = request.form['givenName']
        familyName = request.form['familyName']
        gender = request.form['gender']
        wilaya = request.form['wilaya']
        age = request.form['age']
        dayra = request.form['dayra']
        # symptomes = [i.strip() for i in request.form['symptomes'].split('\n')]
        try:
            _patient = addPatient(givenName, familyName, gender, age, dayra, wilaya, [])
            _consultation = addConsultation(_patient)
            dbCommit()
            return redirect('/consultation/create/asign_symptoms/' + _patient.name)
        except:
            return "Something went wront while saving your consultation"
    else:
        return render_template('create_consultation.html')

@app.route('/consultation/create/asign_symptoms/<id>', methods=['GET', 'POST'])
def asign_symptoms(id):
    _patient = getIndividualByURI(id)
    if request.method == 'POST':
        symptomes = [i.strip() for i in request.form['symptomes'].split('\n')]
        _patient.asignSymptoms(symptomes)
        dbCommit()
        return redirect('/')
    else:
        patientData = {"id": id, "symptomes": "\n".join(symptomsToList(_patient.hasSymptom))}
        return render_template('create_consultation_asign_symptoms.html', patient=patientData)


if __name__ == '__main__':
    app.run(debug=True)
