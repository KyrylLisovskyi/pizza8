import flask
import random
import sqlite3
import requests
import datetime
import flask_wtf
import wtforms
import wtforms.validators
import config

r = random
f = flask
app = flask.Flask(__name__)
app.config.from_object(config.Config)

API = 'b952690ecf4d1fb95f73af0f867ec1d4'
CITY = 'London'

class UserForm(flask_wtf.FlaskForm):
    username = wtforms.StringField("Input username", validators=[wtforms.validators.DataRequired()])
    feedback = wtforms.TextAreaField("Input feedback", validators=[wtforms.validators.DataRequired()])
    submit = wtforms.SubmitField("Submit")

feedbacks = []

@app.route('/feedback/', methods=['GET', 'POST'])
def feedback():
    form = UserForm()
    if form.validate_on_submit():
        feedbacks.append({'name': form.username.data, 'feedback': form.feedback.data})
        flask.flash('Thanks for your feedback!', 'success')
        return flask.redirect(flask.url_for('feedback_list'))
    return flask.render_template('feedback.html', form=form)

@app.route('/feedback_list/')
def feedback_list():
    return flask.render_template('feedback_list.html', feedbacks=feedbacks)

@app.route("/menu/")
def menu():
    connect = sqlite3.connect("datamenu.db")
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM menu")
    data = cursor.fetchall()
    return flask.render_template("menu.html", data=data)

@app.route("/main_page/")
def main_page():
    date = flask.request.args.get('date', default=datetime.date.today().strftime('%Y-%m-%d'))
    weather = get_weather(date)
    return f.render_template("something.html", title="Pizzaria", date=date, weather=weather)

@app.route("/")
def start():
    return f.render_template("login.html", title="Login")

@app.route("/Polls/")
def Polls():
    return f.render_template("poll.html", title="What is your favourite pizza?")

@app.route("/poll_results/")
def poll_results():
    connect = sqlite3.connect("datamenu.db")
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM menu")
    data = cursor.fetchall()
    return f.render_template("poll_results.html", data=data,  title="results for polls")

connect = sqlite3.connect("datamenu.db")
connect.execute('CREATE TABLE IF NOT EXISTS menu (pizza_id TEXT, name TEXT, ingredients TEXT, price TEXT)')

@app.route("/add_pizza/", methods=['GET', 'POST'])
def add_pizza():
    if flask.request.method == "POST":
        name = flask.request.form["name"]
        ingredients = flask.request.form["ingredients"]
        price = flask.request.form["price"]
        pizza_id = flask.request.form["pizza_id"]
        with sqlite3.connect("datamenu.db") as user:
            cursor = user.cursor()
            cursor.execute("INSERT INTO MENU \
            (pizza_id,name,ingredients,price) VALUES (?,?,?,?)",
                           (pizza_id, name, ingredients, price)),
            user.commit()
        return flask.render_template("add_pizza.html")
    else:
        return flask.render_template("add_pizza.html")

def get_weather(date):
    url = f'https://api.openweathermap.org/data/2.5/forecast?q={CITY}&apid={API}&units=metric'
    response = requests.get(url)
    data = response.json()

    if 'list' not in data:
        return 'data loading error'

    forecast = next((item for item in data['list'] if item['dt_txt'].startswith(date)), None)

    if forecast:
        temp = forecast['main']['temp']
        description = forecast['weather'][0]['description']
        return f'temperature: {temp} °C<br>description: {description}'
    else:
        return "can't find data"

app.run(port=55555, debug=True)