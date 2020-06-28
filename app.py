from flask import Flask, render_template, request, redirect
from ontology import onto, consultation, symptoms, patient
from quering_onto import find_v2, getIndividualsByClass, clearIndividualsByClass, addPatient, addConsultation, symptomsToList, dbCommit, getPatient, getConsultationsData, getConsultationData, getIndividualByURI

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/consultations')
def consultations():
    csMap = getIndividualsByClass(onto.consultation)
    # csMap = csMap[1:]
    consultations = getConsultationsData(csMap)
    return render_template('consultations.html', consultations=consultations)


@app.route('/consultation/<id>', methods=['GET', 'POST'])
def consultation(id):
    consultation = getIndividualByURI(id)
    consultationData = getConsultationData(consultation)
    print(consultationData)
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
            patients = find_v2(onto.patient, {
                "givenName": givenName,
                "familyName": familyName
            })
            _patient = None
            if len(patients) == 0:
                _patient = addPatient(givenName, familyName,
                                      gender, age, dayra, wilaya, [])
            else:
                _patient = patients[0]
            _consultation = addConsultation(_patient)
            dbCommit()
            return redirect('/consultation/create/asign_symptoms/' + _consultation.name + "/" + _patient.name)
        except:
            return "Something went wront while saving your consultation"
    else:
        return render_template('create_consultation.html')


@app.route('/consultation/create/asign_symptoms/<idconsultation>/<idpatient>', methods=['GET', 'POST'])
def asign_symptoms(idconsultation, idpatient):
    _patient = getIndividualByURI(idpatient)
    _consultation = getIndividualByURI(idconsultation)
    if request.method == 'POST':
        symptomes = [i.strip() for i in request.form['symptomes'].strip().split(
            '\n') if len(i.strip()) > 0]
        _patient.asignNewSymptoms(symptomes)
        _consultation.asignNewSymptoms(symptomes)
        dbCommit()
        return redirect('/')
    else:
        patientData = {
            "id": idpatient,
            "symptomes": "\n".join(symptomsToList(_patient.hasSymptom)),
            "idconsultation": idconsultation}
        return render_template('create_consultation_asign_symptoms.html', patient=patientData)


@app.route('/clearall')
def clearAll():
    clearIndividualsByClass(onto.symptoms)
    clearIndividualsByClass(onto.patient)
    clearIndividualsByClass(onto.consultation)
    dbCommit()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
