from flask import Flask
from flask import g
from database import Base, engine

#def create_app():
app = Flask(__name__)
app.secret_key = '9d2b7fce449ec7d3add311b3408106b8'
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

#return app

if __name__ == "__main__":
    with app.app_context():
        """try:
            Base.metadata.create_all(bind=engine)
            print("Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")"""
    app.run(debug=True)

"""
app.register_blueprint(auth.bp)
#app.register_blueprint(blog.bp)

# make url_for('index') == url_for('blog.index')
# in another app, you might define a separate main index here with
# app.route, while giving the blog blueprint a url_prefix, but for
# the tutorial the blog will be the main index
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
    app.run() """