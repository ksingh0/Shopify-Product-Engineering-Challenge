#Kris Singh May 22nd 2022

#imports
from tkinter import CENTER
from flask import Flask, redirect, url_for, render_template, request, session, flash, send_file
from datetime import timedelta
from numpy import less_equal
import pandas as pd
import requests
import json

itemList = []
validCities = ["Toronto", "Vancouver", "Calgary", "Winnipeg", "Montreal"]
app = Flask(__name__)
app.secret_key = "key"
app.permanent_session_lifetime = timedelta(minutes = 5)

#Create the homepage
@app.route("/", methods = ["POST","GET"])
def home():
    #If anything was submitted execute this code
    if request.method == "POST":
        #get the inputs for item, city, and amount
        item = request.form.get("item")
        city = request.form.get("city")
        number = request.form.get("number")
        #make sure an item was given in the first place
        if item == '':
            flash("Please enter an item")
            return render_template("index.html", PageTitle = "Home")
        #make sure the city is valid
        if city not in validCities :
            flash("Please enter a valid city")
            return render_template("index.html", PageTitle = "Home")
        #Since we know there is a valid city, we can get the weather
        weather = getWeather(city)

        #make sure there is a number present
        if number == '':
            flash("Please enter a valid number greater than 0")
            return render_template("index.html", PageTitle = "Home")
        number = int(number)
        #create a dictionary for the 4 fields
        inventory = {'Item':item,'City':city,'Amount':number, 'Weather':weather}
        #check if there is already a dictionary for the given item and city and if so add the amount
        for i in itemList:
            if i['Item'] == item and i['City'] == city:
                i['Amount'] = i['Amount'] + number
                updateList()
                item = ''
                city = ''
                number = ''
                weather = ''
                return render_template("index.html",PageTitle = "Home")
        #if it doesnt exist append it to the list of items and clear vars
        itemList.append(inventory)
        item = ''
        city = ''
        number = ''
        weather = ''
    #refresh the page with the new list
    updateList()
    return render_template("index.html",PageTitle = "Home")

@app.route("/delete", methods = ["POST","GET"])
def delete():
    if request.method=="POST":
        #get the inputs for item and city
        item = request.form.get("item")
        city = request.form.get("city")
        #make sure an item was given in the first place
        if item == '':
            flash("Please enter an item")
            return render_template("delete.html", PageTitle = "Delete")
        #make sure the city is valid
        if city not in validCities :
            flash("Please enter a valid city")
            return render_template("delete.html", PageTitle = "Delete")
        #iterate through the list to find what needs to be deleted
        for i in itemList:
            if i['Item'] == item and i['City'] == city:
                itemList.remove(i)
                updateList()
                return render_template("delete.html",PageTitle = "Delete")
        flash("That inventory does not exist.")
        return render_template("delete.html",PageTitle = "Delete")
    updateList()
    return render_template("delete.html",PageTitle = "Delete")

@app.route("/view")
def view():
    if request.method=="POST":
        #get the inputs for item,city, and amount
        item = request.form.get("item")
        city = request.form.get("city")
        #make sure an item was given in the first place
        if item == '':
            flash("Please enter an item")
            return render_template("delete.html", PageTitle = "Delete")
        #make sure the city is valid
        if city not in validCities :
            flash("Please enter a valid city")
            return render_template("delete.html", PageTitle = "Delete")
        #iterate through the list to find what needs to be deleted
        for i in itemList:
            if i['Item'] == item and i['City'] == city:
                itemList.remove(i)
                updateList()
                return render_template("delete.html",PageTitle = "Delete")
        flash("That inventory does not exist.")
        return render_template("delete.html",PageTitle = "Delete")
    updateList()
    return render_template("view.html",PageTitle = "Inventory")

@app.route("/edit", methods = ["POST","GET"])
def edit():
    if request.method == "POST":
        #get the inputs for item, city, and amount
        item = request.form.get("item")
        city = request.form.get("city")
        number = request.form.get("number")
        #make sure an item was given in the first place
        if item == '':
            flash("Please enter an item")
            return render_template("edit.html", PageTitle = "Edit")
        #make sure the city is valid
        if city not in validCities :
            flash("Please enter a valid city")
            return render_template("edit.html", PageTitle = "Edit")

        #make sure there is a number present
        if number == '':
            flash("Please enter a valid number greater than 0")
            return render_template("edit.html", PageTitle = "Edit")
        number = int(number)

        #search for the inventory
        for i in itemList:
            if i['Item'] == item and i['City'] == city:
                i['Amount'] = number
                updateList()
                item = ''
                city = ''
                number = ''
                return render_template("edit.html",PageTitle = "Edit")
        #if it doesnt exist notify the user
        flash("No such inventory exists")
    #refresh the page with the new list
    updateList()
    return render_template("edit.html",PageTitle = "Edit")
    
@app.route('/download')
def download():
    createcsv()
    return send_file('inventory.csv', as_attachment=True)

def createcsv():
    df = pd.DataFrame(itemList)
    df.to_csv('inventory.csv')

def getWeather(city):
    if city == "Toronto":
        weatherCall = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=43.6532&lon=-79.3832&appid=cbbd91c1e47fde97c73a0ab147b470c7&units=metric")
    elif city == "Vancouver":
        weatherCall = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=49.246292&lon=-123.116226&appid=cbbd91c1e47fde97c73a0ab147b470c7&units=metric")
    elif city == "Calgary":
        weatherCall = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=51.049999&lon=-114.066666&appid=cbbd91c1e47fde97c73a0ab147b470c7&units=metric")
    elif city == "Winnipeg":
        weatherCall = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=49.895077&lon=-97.138451&appid=cbbd91c1e47fde97c73a0ab147b470c7&units=metric")
    elif city == "Montreal":
        weatherCall = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=45.508888&lon=-73.561668&appid=cbbd91c1e47fde97c73a0ab147b470c7&units=metric")
    hold = weatherCall.text
    weatherInfo = json.loads(hold)
    desc = weatherInfo['weather'][0]['description']
    temp = weatherInfo['main']['temp']
    weather = "Weather Decription: " + desc + "    Temp(Celcius): " + str(temp)
    return weather

def updateList():
    df = pd.DataFrame(itemList)
    df.to_html('templates/inventory.html', render_links = True,justify=CENTER, escape = False)

if __name__ == "__main__":
    itemList = []
    inventory = {}
    updateList()
    createcsv()
    app.run()
