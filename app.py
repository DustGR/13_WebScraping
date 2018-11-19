from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import mars_scraping

app = Flask(__name__)
#flask_pymongo sets up mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/mission_to_mars"
mongo = PyMongo(app)

@app.route("/")
def index():
    mars_scrape = mongo.db.web_data.find_one()
    return render_template("index.html", data=mars_scrape)

@app.route("/scrape")
def scrape():
    data = mongo.db.web_data
    scrape_return = mars_scraping.scrape()
    data.update({}, {"$set" : scrape_return})
    return redirect("/", code=302)

if __name__ == "__main__":
    app.run(debug=True)