from flask import Flask, render_template, request, redirect
from quering_onto import addPatient, addConsultation, dbCommit, getPatient
from ontology import onto, consultation

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/consultations', methods=['GET', 'POST'])
def cs():
    if request.method == 'POST':
        pass
    else:
        # consultations = [
        #     {
        #         "patient": {
        #             "firstName": "Abdelhak",
        #             "familyName": "Ihadjadene",
        #             "gender": "Male"
        #         },
        #         "date": "06-24-2020",
        #         "output": "He DIES"
        #     }
        # ]
        csMap = onto.search(iri="*consultation*")
        csMap = csMap[1:]
        consultations = []
        for i in csMap:
            iri_p = str(i.hasPatient).split('out.')[-1]
            pat = getPatient(iri_p)
            consultations.append({
                "patient": {
                    "givenName": pat.givenName,
                    "familyName": pat.familyName,
                    "gender": pat.gender,
                    "wilaya": pat.wilaya,
                    "dayra": pat.dayra,
                    "age": pat.age
                },
                "date": i.date,
                "output": i.output
            })
        return render_template('consultation.html', consultations=consultations)


@app.route('/consultation', methods=['GET', 'POST'])
def consultation():
    if request.method == 'POST':
        givenName = request.form['givenName']
        familyName = request.form['familyName']
        gender = request.form['gender']
        wilaya = request.form['wilaya']
        age = request.form['age']
        dayra = request.form['dayra']
        symptomes = [i.strip() for i in request.form['symptomes'].split('\n')]
        _patient = addPatient(givenName, familyName, gender,
                              age, dayra, wilaya, symptomes)
        _consultation = addConsultation(_patient)
        dbCommit()
        return redirect('/')
    else:
        return render_template('consultation_template.html')


if __name__ == '__main__':
    app.run(debug=True)
