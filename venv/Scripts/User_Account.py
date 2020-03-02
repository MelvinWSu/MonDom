from flask_login import UserMixin
import pyrebase

firebaseConfig = {
    "apiKey": "os.environ['FIREBASE_API_KEY']",
    "authDomain": "mondom-97740.firebaseapp.com",
    "databaseURL": "https://mondom-97740.firebaseio.com",
    "projectId": "mondom-97740",
    "storageBucket": "mondom-97740.appspot.com",
    "messagingSenderId": "877143682729",
    "appId": "1:877143682729:web:54f672e485632c73ad43b8",
    "measurementId": "G-6S2J42P9KP"
};

firebase = pyrebase.initialize_app(firebaseConfig)


class User(UserMixin):
    def __init__(self, id_, name, email):
        self.id = id_
        self.name = name
        self.email = email

    def retrieve(user_id):
        all_users = firebase.database().child("users").get()
        if (all_users.val() != None):
            for users in all_users.each():
                if (users.val().get("uid") == user_id):
                    print("Found account")
                    return User(users.val().get("uid"), users.val().get("name"), users.val().get("email"))
            print("Did not find account")
            return None

    def new_account(id_, name, email):
        data = {
            "uid": id_,
            "name": name,
            "email": email
        }
        db = firebase.database()
        db.child("users").push(data)
