from flask import Flask, render_template, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user
)
import pyrebase
from oauthlib.oauth2 import WebApplicationClient
import requests
import os
import json
from User_Account import User

firebaseConfig = {
    "apiKey": "os.environ['FIREBASE_API_KEY']",
    "authDomain": "temp-2705a.firebaseapp.com",
    "databaseURL": "https://temp-2705a.firebaseio.com",
    "projectId": "temp-2705a",
    "storageBucket": "temp-2705a.appspot.com",
    "messagingSenderId": "435714692697",
    "appId": "1:435714692697:web:f3798425850b8a1b"
};

firebase = pyrebase.initialize_app(firebaseConfig)

GOOGLE_CLIENT_ID = '186867853070-u1t7tl6c7fo3glhi11013tncudk71hbs.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET = 'uJbdlqfYu1xsHBrOjhRNCl0c'
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)

client = WebApplicationClient(GOOGLE_CLIENT_ID)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


@login_manager.user_loader
def load_user(user_id):
    return User.retrieve(user_id)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

"""root should no longer be accessed, use home as default url"""
@app.route("/")
def index():
    if current_user.is_authenticated:
        return (
            "<p>Helloo, {}! You're logged in! Email: {}</p>"
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email
            )
        )
    else:
        return ('<body><a class="button" href="/login">Google Login</a><a class="button" href="/home">home</a><a class="button" href="/test">test</a></body>')


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()

    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    # Create a user in your db with the information provided
    # by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email
    )

    # Doesn't exist? Add it to the database.
    if not User.retrieve(unique_id):
        User.new_account(unique_id, users_name, users_email)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("profile"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/test')
def test_page():
    return render_template("test.html")


@app.route("/home")
def home():
    return render_template("home.html", user = current_user)

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user = current_user)

@app.route("/profile", methods = ['Get','POST'])
def profile_post():
    print("stuff")
    text = request.form['text']
    processed_text = text.upper()
    print (processed_text)
    """all_users = firebase.database().child("users").get()
    if (all_users.val() != None):
        for users in all_users.each():
            if (users.val().get("uid") == current_user.uid):
                firebase.database().child("users").child(users.key).child("saved").update(text)"""


if __name__ == "__main__":
    app.run(debug=True)
