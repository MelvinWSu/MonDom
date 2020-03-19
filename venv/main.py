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
import datetime
import base64
from email_control import create_message, send_message

firebaseConfig = {
  "apiKey": "AIzaSyDUo_HsIYMSJRBfMqeK3e3jj6mjckt1Oq4",
  "authDomain": "mondom.firebaseapp.com",
  "databaseURL": "https://mondom.firebaseio.com",
  "projectId": "mondom",
  "storageBucket": "mondom.appspot.com",
  "messagingSenderId": "258322858492",
  "appId": "1:258322858492:web:fdb57668431af72a08f279",
  "measurementId": "G-8S5ZYLERJW"
};

firebase = pyrebase.initialize_app(firebaseConfig)

GOOGLE_CLIENT_ID = os.environ['GOOGLE_CLIENT_ID']
GOOGLE_CLIENT_SECRET = os.environ['GOOGLE_CLIENT_SECRET']
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

login_manager = LoginManager()
login_manager.init_app(app)

api_key = os.environ["GOOGLE_API_KEY"]
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
    send_emails("106141010986049248632")
    if current_user.is_authenticated:
        return (
            "<p>Helloo, {}! You're logged in! Email: {}</p>"
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email
            )
        )
    else:

        return ('<body>'
                '<a class="button" href="/login">Google Login</a>'
                '<a class="button" href="/home">home</a>'
                '<a class="button" href="/test">test</a>'
                '</body>'
                '<body>'
                '<a class="button" href="/home">Go to home page</a>'
                '</body>'
                )


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
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/home")
def home():
    self_url = get_self_url()
    return render_template("home.html", user = current_user, current_page = self_url)

@app.route("/profile")
@login_required
def profile():
    self_url = get_self_url()
    temp_list = get_recent_list(current_user.id)
    favorite_list = get_favorites_list(current_user.id)
    favorite_list = list(zip(favorite_list,return_website(favorite_list)))
    return render_template("profile.html", user=current_user, recent_searched_websites = temp_list,favorite_list = favorite_list, current_page = self_url)

@app.route("/profile", methods = ['POST'])
@login_required
def profile_post():
    self_url = get_self_url()
    text = request.form.get('search_input', "")
    add_to_favorite = request.form.get('add_to_favorite', "")
    website_result = ""
    if (text != ""):
        text = "http://" + text
        # check input
        website_result = check_website(text, current_user.id)
        #get recent searches
    elif (add_to_favorite != ""):
        add_website_favorite(current_user.id, add_to_favorite)
    recent_list = get_recent_list(current_user.id)
    favorite_list = get_favorites_list(current_user.id)
    favorite_list = list(zip(favorite_list,return_website(favorite_list)))
    return render_template("profile.html", user=current_user, recent_searched_websites = recent_list, website_info = website_result, favorite_list = favorite_list, current_page = self_url)

@app.route("/profile/settings")
@login_required
def settings():
    self_url = get_self_url()
    email_freq = get_email_freq(current_user.id)
    return render_template("profile_settings.html", user=current_user, email_freq=email_freq, current_page=self_url)

@app.route("/profile/settings", methods=['POST'])
@login_required
def settings_update():
    text = request.form.get('input', "")
    text2 = request.form.get('send', "")
    print(text2)
    email_good = False
    if (text != None):
        change_email_freq(current_user.id, text)
    if (text2):
        email_good = send_emails(current_user.id)
    self_url = get_self_url()
    email_freq = get_email_freq(current_user.id)
    return render_template("profile_settings.html", user=current_user, email_freq=email_freq, current_page=self_url, email_good=email_good)

@app.route("/profile/list_managment")
@login_required
def list_managment():
    favorite_list = get_detailed_favorites_list(current_user.id)
    only_favs = []
    only_prio = []
    for temp in favorite_list:
        only_favs.append(temp[0])
        only_prio.append(temp[1])
    favorite_list = zip(only_favs, return_website(only_favs), only_prio)
    self_url = get_self_url()
    return render_template("list_managment.html", user=current_user, favorite_list=favorite_list, current_page=self_url)

@app.route("/profile/list_managment", methods = ['POST'])
@login_required
def list_managment_update():
    text = request.form.get('cmd', "")
    input = text.split(",")
    update_favorite(current_user.id, input[0], input[1])
    favorite_list = get_detailed_favorites_list(current_user.id)
    only_favs = []
    only_prio = []
    for temp in favorite_list:
        only_favs.append(temp[0])
        only_prio.append(temp[1])
    favorite_list = zip(only_favs, return_website(only_favs), only_prio)
    self_url = get_self_url()
    return render_template("list_managment.html", user=current_user, favorite_list=favorite_list, current_page=self_url)

"""check website if it exist, if so add it to recent searches and return true. else, return false"""
def check_website(input, id):
    specific_user = firebase.database().child("users").child(id).child("recent_searched_websites").get()
    if (specific_user.val() != None):
        for website_entry in specific_user.each():
            if (website_entry.val() == input):
                now = datetime.datetime.now()
                time_str = now.strftime("%Y%m%d%H%M%S")
                firebase.database().child("users").child(id).child("recent_searched_websites").child(website_entry.key()).remove()
                firebase.database().child("users").child(id).child("recent_searched_websites").update({time_str: input})
                return get_website_info(input)
    payload = {"client": {'clientId': "", 'clientVersion': ""},
               "threatInfo": {'threatTypes': ["THREAT_TYPE_UNSPECIFIED", "MALWARE", "SOCIAL_ENGINEERING",
                                              "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                              'platformTypes': ["PLATFORM_TYPE_UNSPECIFIED", "WINDOWS", "LINUX", "ANDROID", "OSX",
                                                "IOS",
                                                "ANY_PLATFORM", "ALL_PLATFORMS", "CHROME"],
                              'threatEntryTypes': ["THREAT_ENTRY_TYPE_UNSPECIFIED", "URL", "EXECUTABLE"],
                              'threatEntries': [{'url': input}]
                              }
               }
    r = requests.post("https://safebrowsing.googleapis.com/v4/threatMatches:find", params={'key': api_key}, json=payload)
    print(r)
    print(r.json())
    now = datetime.datetime.now()
    time_str = now.strftime("%Y%m%d%H%M%S")
    info = {
        "url": input,
        "last_update": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        "IP_address": "000.000.000.000"
    }
    website_entry = firebase.database()

    website_entry.child("database").child(base64.b64encode(bytes(input, "utf-8"))).child("safebrowsing").set(r.json())
    website_entry.child("database").child(base64.b64encode(bytes(input, "utf-8"))).update(info)
    firebase.database().child("users").child(id).child("recent_searched_websites").update({time_str : input})
    return get_website_info(input)


def add_website_favorite(id,input):
    specific_user = firebase.database().child("users").child(id).child("favorited_websites").get()
    if (specific_user.val() != None):
        for website in specific_user.each():
            if (website.val() == input):
                return True
    b64encoded = base64.b64encode(bytes(input, "utf-8"))
    firebase.database().child("users").child(id).child("favorited_websites").child(b64encoded).set({"priority":"normal"})

def get_favorites_list(id):
    temp_list = []
    the_user = firebase.database().child("users").child(id).child("favorited_websites").get()
    if (the_user.val() != None):
        for entry in the_user.each():
            p2 = base64.b64decode(entry.key()[1:]).decode()
            temp_list.append(p2)
    return temp_list

def get_detailed_favorites_list(id):
    temp_list = []
    the_user = firebase.database().child("users").child(id).child("favorited_websites").get()
    if (the_user.val() != None):
        for entry in the_user.each():
            p2 = []
            p2.append(base64.b64decode(entry.key()[1:]).decode())
            p2.append(entry.val())
            temp_list.append(p2)
    return temp_list

def get_recent_list(id):
    temp_list = []
    the_user = firebase.database().child("users").child(id).child("recent_searched_websites").get()
    if (the_user.val() != None):
        for entry in the_user.each():
            temp_list.append(entry.val())
    temp_list = list(reversed(temp_list))
    return temp_list

def get_website_info(website):
    b64encoded = base64.b64encode(bytes(website, "utf-8"))
    website_results = firebase.database().child("database").child(b64encoded).child("safebrowsing").get()
    return website_results.val()

def get_self_url():
    temp_str = request.url
    temp_str = temp_str.replace("http://127.0.0.1:5000/","")
    return(temp_str)

def return_website(website_list):
    results = []
    for website in website_list:
        b64encoded = base64.b64encode(bytes(website, "utf-8"))
        website_results = firebase.database().child("database").child(b64encoded).child("safebrowsing").get()
        if website_results.val() is not None:
            results.append(True)
        else:
            results.append(False)
    return results

def update_favorite(id, website, cmd):
    b64encoded = base64.b64encode(bytes(website, "utf-8"))
    if (cmd == 'del'):
        firebase.database().child("users").child(id).child("favorited_websites").child(b64encoded).remove()
    elif(cmd == "1"):
        firebase.database().child("users").child(id).child("favorited_websites").child(b64encoded).update({"priority":"no"})
    elif (cmd == "2"):
        firebase.database().child("users").child(id).child("favorited_websites").child(b64encoded).update({"priority": "normal"})
    elif (cmd == "3"):
        firebase.database().child("users").child(id).child("favorited_websites").child(b64encoded).update({"priority": "emer"})

def get_email_freq(id):
    the_user = firebase.database().child("users").child(id).child("email_freq").get()
    return(the_user.val())

def change_email_freq(id, num):
    firebase.database().child("users").child(id).update({"email_freq":num})


def send_emails(id):
    the_user = firebase.database().child("users").child(id)
    now = datetime.datetime.now()
    email = the_user.child("email").get().val()
    email_freq = the_user.child("email_freq").get().val()
    last_time = the_user.child("last_time").get().val()
    time_str = now.strftime("%Y%m%d")
    message = create_message("mondomsecure@gmail.com", email, "Test Email", "This is a test email")
    send_message(message=message)
    firebase.database().child("users").child(id).update({"last_time":time_str})
    """the_user = firebase.database().child("users").get()
    if (the_user.val() != None):
        for entry in the_user.each():
            print(entry.val().get("email"))
            message = create_message("mondomsecure@gmail.com", "msu009@ucr.edu", "Test Email", "This is a test email")
            send_message(message=message)"""
    return True

def gentext(id):
    message = ''
    print(message)

if __name__ == "__main__":
    app.run(debug=True)