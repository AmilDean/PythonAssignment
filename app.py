import requests as requests
from flask import Flask, render_template, request, url_for
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField,DateField
from pymongo import MongoClient


app = Flask(__name__)
app.config["SECRET_KEY"]="COP4813"
app.config["MONGO_URI"] = "mongodb+srv://abadr013:6080074@learningmongodb.gbaie.mongodb.net/mySecondDatabase?retryWrites=true&w=majority"
mongo = PyMongo(app)

class Expenses(FlaskForm):
    description = StringField("description")
    category = SelectField('Type',
                           choices=[('Car', 'Car'),
                                    ('Food', 'Food'),
                                    ('Medical', 'Medical'),
                                    ('College', 'College'),
                                    ('Other', 'Other')
                                    ])
    cost = DecimalField(label='label',description="cost")
    currency = SelectField('Currency',
                             choices=[('USD', 'USD'),
                                      ('USDAUD', 'AUD'),
                                      ('USDCAD', 'CAD'),
                                      ('USDPLN', 'PLN'),
                                      ('USDAED', 'AED')])
    date = DateField("Date",format='%Y-%m-%d')

def get_total_expenses(category):
    my_expenses2 = mongo.db.expenses.find({"category" : category})
    total_cost2 = 0
    for i in my_expenses2:
        total_cost2 += float(i["cost"])
    return total_cost2

def currency_converter(cost,currency):
    url="http://api.currencylayer.com/live?access_key=eb3eb721efa04b79a66a97c01e5b5006"
    response = requests.get(url).json()
    if currency != 'USD':
        float_cost = float(cost) / float(response["quotes"][currency])
        converted_cost = "{:.2f}".format(float_cost)
    else:
        return cost
    return converted_cost

@app.route('/')
def index():
    my_expenses = mongo.db.expenses.find()
    total_cost=0
    for i in my_expenses:
        total_cost+=float(i["cost"])
    expensesByCategory = [
        ("Car" , get_total_expenses("Car")),
        ("Food", get_total_expenses("Food")),
        ("Medical", get_total_expenses("Medical")),
        ("College", get_total_expenses("College")),
        ("Other", get_total_expenses("Other"))]
    return render_template("index.html", expenses=total_cost, expensesByCategory=expensesByCategory)

@app.route('/addExpenses',methods=["GET","POST"])
def addExpenses():
    expensesForm = Expenses(request.form) # INCLUDE THE FORM
    if request.method == "POST":
        description = request.form["description"]
        category = request.form["category"]
        cost = request.form["cost"]
        date = request.form["date"]
        currency = request.form["currency"]
        converted_cost = currency_converter(cost, currency)
        pyDict = {'description': description,
                  'category': category,
                  'cost': converted_cost,
                  'date': date,
                  'currency': currency}
        mongo.db.expenses.insert_one(pyDict)
        return render_template("expenseAdded.html")
    return render_template("addExpenses.html",form=expensesForm)



app.run(port=5000)