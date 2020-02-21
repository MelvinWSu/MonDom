from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def main_page():
    return 'Main Menu'

@app.route('/teacher')
def hello_teacher():
    return 'Hey Teacher'


@app.route('/students/<student>')
def hello_students(student):
    return 'Hello %s as student' % student


@app.route('/user/<name>')
def hello_user(name):
    if name == 'teacher':
        return redirect(url_for('hello_teacher'))
    else:
        return redirect(url_for('hello_students'))

@app.route('/Test')
def test_page():
    return render_template('Test.html')

@app.route('/<string:page_name>/')
def render_static(page_name):
    return render_template('%s.html' % page_name)

if __name__ == "__main__":
    app.run(debug=True)
