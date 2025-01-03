from flask import Flask
from flask import g
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# apply the blueprints to the app
import auth
import portfolio
app.register_blueprint(auth.bp)
app.register_blueprint(portfolio.bp)
app.add_url_rule("/", endpoint="index")

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

if __name__ == "__main__":
    with app.app_context():
        app.run(debug=True)