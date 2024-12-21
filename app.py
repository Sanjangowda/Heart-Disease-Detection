import joblib
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import pandas as pd
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

#filename = 'diabetes-prediction-rfc-model.pkl'
#classifier = pickle.load(open('diabetes-prediction-rfc-model.pkl', 'rb'))
model = pickle.load(open('trained_model.pkl', 'rb'))
#model1 = pickle.load(open('model1.pkl', 'rb'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/help')
def help():
    return render_template("help.html")


@app.route('/terms')
def terms():
    return render_template("tc.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        return render_template("login.html", form=form)
    return render_template("login.html", form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
  form = RegisterForm()
  if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            error_message = "Username or email already exists. Please choose another."
            return render_template('signup.html', form=form, error=error_message)

        # If no duplicate, proceed to create a new user
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")
  return render_template('signup.html', form=form)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/disindex")

def disindex():
    return render_template("disindex.html")





@app.route("/heart")
@login_required
def heart():
    return render_template("heart.html")





@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))





############################################################################################################

@app.route('/predictheart', methods=['POST'])
def predictheart():
    input_features = [float(x) for x in request.form.values()]
    features_value = [np.array(input_features)]

    features_name = ["age", "sex", "cp", "trestbps", "chol", "fbs",
                     "restecg", "thalach", "exang", "oldpeak", "slope", "ca",
                     "thal"]

    df = pd.DataFrame(features_value, columns=features_name)
    output = model.predict(df)

    if output == 1:
        res_val = "a high risk of Heart Disease"
    else:
        res_val = "a low risk of Heart Disease"
    
     # Extract individual inputs for a detailed report
    report_data = {
        "age": input_features[0],
        "trestbps": input_features[1],
        "cholesterol": input_features[2],
        "max_heart_rate": input_features[3],
        "oldpeak": input_features[4],
        "sex": "Male" if input_features[5] == 1 else "Female",
        "result": res_val
    }

    # Additional analysis (example ranges; adjust based on medical data)
    report_data["blood_pressure_status"] = "Normal" if 90 <= input_features[1] <= 120 else "High"
    report_data["cholesterol_status"] = "Healthy" if input_features[2] < 200 else "High"
    report_data["heart_rate_status"] = "Healthy" if input_features[3] > 60 and input_features[3] < 100 else "Abnormal"


    username = current_user.username
    return render_template('report.html', report_data=report_data, username=username)



############################################################################################################



if __name__ == "__main__":
    app.run(debug=True)

