from flask import Flask, render_template, request, redirect, flash, send_from_directory, Response
from ontology import onto, consultation, symptoms, patient
from owlready2 import *
from quering_onto import CSV_consultations, CSV_patients, find_v2, getPatientData, getIndividualsByClass, clearIndividualsByClass, addPatient, addConsultation, opToList, dbCommit, getPatient, getConsultationsData, getConsultationData, getIndividualByURI

app = Flask(__name__)
app.secret_key = 'sdhfbsdlfgqbdlfgibsdlfkhgbwdf'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/as_doctor')
def as_doctor():
    return render_template('as_doctor.html')


@app.route('/as_patient')
def as_patient():
    return render_template('as_patient.html')


@app.route('/consultations')
def consultations():
    csMap = find_v2(onto.consultation)
    consultations = getConsultationsData(csMap)
    return render_template('consultations.html', consultations=consultations)


@app.route('/consultations/<id>', methods=['GET', 'POST'])
def consultation(id):
    # consultation = getIndividualByURI(id)
    consultation = find_v2(onto.consultation, {"name": id})
    if len(consultation) == 0:
        flash("This consultation doesn't exist", 'error')
        return redirect('/consultations')
    consultation = consultation[0]
    consultationData = getConsultationData(consultation)
    if request.method == 'POST':
        # print(request.form['output'].split('\n'))
        consultation.output = request.form['output'].replace('\r', '')
        dbCommit()
        return redirect("/consultations")
    else:
        return render_template('consultation.html', consultation=consultationData)


@app.route('/consultations/<id>/delete')
def deleteConsultation(id):
    consultation = find_v2(onto.consultation, {"name": id})
    if len(consultation) == 0:
        flash("This consultation doesn't exist", 'error')
        return redirect('/consultations')
    consultation = consultation[0]
    destroy_entity(consultation)
    dbCommit()
    return redirect('/consultations')


@app.route('/patient', methods=['GET', 'POST'])
def patient():
    if request.method == 'POST':
        givenName = request.form['givenName']
        familyName = request.form['familyName']
        age = request.form['age']
        gender = request.form['gender']
        _patient = find_v2(onto.patient, {
            "givenName": givenName,
            "familyName": familyName,
            "age": age,
            "gender": gender
        })
        if len(_patient) == 0:
            flash(f'No patient named {givenName} {familyName}', 'error')
            return redirect('/patient')
        else:
            return redirect('/patient_consultations/' + _patient[0].name)
    else:
        return render_template('patient.html')


@app.route('/patient_consultations/<idpatient>')
def patient_consultations(idpatient):
    _patient = find_v2(onto.patient, {"name": idpatient})
    if len(_patient) == 0:
        flash('Patient Not Found', 'error')
        return redirect('/patient')
    _patient = _patient[0]
    csMap = _patient.hadConsultation
    consultations = getConsultationsData(csMap)
    return render_template('patient_consultations.html', patient=getPatientData(_patient), consultations=consultations)


@app.route('/consultation_check/<id>')
def consultation_check(id):
    consultation = find_v2(onto.consultation, {"name": id})
    if len(consultation) == 0:
        flash('Consultation Not Found', 'error')
        return redirect('/')
    consultation = consultation[0]
    consultationData = getConsultationData(consultation)
    return render_template('consultation_check.html', consultation=consultationData)


@app.route('/consultation/create', methods=['GET', 'POST'])
def createConsultation():
    if request.method == 'POST':
        givenName = request.form['givenName']
        familyName = request.form['familyName']
        gender = request.form['gender']
        wilaya = request.form['wilaya']
        age = request.form['age']
        try:
            patients = find_v2(onto.patient, {
                "givenName": givenName,
                "familyName": familyName
            })
            _patient = None
            if len(patients) == 0:
                _patient = addPatient(givenName, familyName,
                                      gender, age, wilaya, [])
            else:
                _patient = patients[0]
            _consultation = addConsultation(_patient)
            dbCommit()
            return redirect('/consultation/create/asign_symptoms/' + _consultation.name + "/" + _patient.name)
            # return redirect('/consultation/create')
        except Exception as e:
            print(str(e))
            return "Something went wrong while saving your consultation"
    else:
        w = find_v2(onto.wilaya)
        wilayas = [i.wilayaName for i in w]
        return render_template('create_consultation.html', wilayas=wilayas)


@app.route('/consultation/create/asign_symptoms/<idconsultation>/<idpatient>', methods=['GET', 'POST'])
def asign_symptoms(idconsultation, idpatient):
    _patient = getIndividualByURI(idpatient)
    _consultation = getIndividualByURI(idconsultation)
    if request.method == 'POST':
        symps = request.form.getlist('symptoms[]')
        symptomes = [i.strip() for i in symps if len(i.strip()) > 0]
        _patient.asignNewSymptoms(symptomes)
        _consultation.asignNewSymptoms(symptomes)
        dbCommit()
        return redirect('/consultation/create/asign_diseases/' + idconsultation + "/" + idpatient)

    else:
        patientData = {
            "id": idpatient,
            "symptomes": opToList(_patient.hasSymptom),
            "idconsultation": idconsultation}
        return render_template('create_consultation_asign_symptoms.html', patient=patientData)


@app.route('/consultation/create/asign_diseases/<idconsultation>/<idpatient>', methods=['GET', 'POST'])
def asign_diseases(idconsultation, idpatient):
    _patient = getIndividualByURI(idpatient)
    if request.method == 'POST':
        chrons = request.form.getlist('diseases[]')
        chronics = [i.strip() for i in chrons if len(i.strip()) > 0]
        _patient.asignNewDiseases(chronics)
        dbCommit()
        print(_patient.hasDisease)
        return redirect('/consultation/create/asign_traitments/' + idconsultation + "/" + idpatient)
    else:
        patientData = {
            "id": idpatient,
            "diseases": opToList(_patient.hasDisease),
            "idconsultation": idconsultation}
        return render_template('create_consultation_asing_diseases.html', patient=patientData)


@app.route('/consultation/create/asign_traitments/<idconsultation>/<idpatient>', methods=['GET', 'POST'])
def asign_traitments(idconsultation, idpatient):
    _patient = getIndividualByURI(idpatient)
    if request.method == 'POST':
        traits = request.form.getlist('traitments[]')
        T = [i.strip() for i in traits if len(i.strip()) > 0]
        _patient.asignNewTraitments(T)
        dbCommit()
        return redirect('/')
    else:
        patientData = {
            "id": idpatient,
            "traitments": opToList(_patient.hasTraitment),
            "idconsultation": idconsultation}
        return render_template('create_consultation_asing_traitments.html', patient=patientData)


@app.route('/clear/<what>')
def clearAll(what):
    if what == "patients":
        clearIndividualsByClass(onto.patient)
    elif what == "consultations":
        clearIndividualsByClass(onto.consultation)
    elif what == "symptoms":
        clearIndividualsByClass(onto.symptoms)
    elif what == 'diseases':
        clearIndividualsByClass(onto.diseases)
    elif what == 'traitments':
        clearIndividualsByClass(onto.traitments)
    elif what == 'all':
        clearIndividualsByClass(onto.patient)
        clearIndividualsByClass(onto.consultation)
        clearIndividualsByClass(onto.symptoms)
        clearIndividualsByClass(onto.diseases)
        clearIndividualsByClass(onto.traitments)
    dbCommit()
    return redirect('/')


@app.route('/download/<file>')
def download(file):
    if file == "patients":
        CSV_patients()
        return send_from_directory('./', 'patients.csv', as_attachment=True)
    elif file == "consultations":
        CSV_patients()
        return send_from_directory('./', 'consultations.csv', as_attachment=True)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
