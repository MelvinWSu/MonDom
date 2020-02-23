from flask_login import UserMixin
import pyrebase

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
                    return User(users.val().get("uid"), users.val().get("name"), users.val().get("email"))
                return None

    def new_account(id_, name, email):
        data = {
            "uid": id_,
            "name": name,
            "email": email
        }
        db = firebase.database()
        db.child("users").push(data)
