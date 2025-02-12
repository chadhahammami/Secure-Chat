
from flask import Blueprint, render_template, request, url_for, redirect, session, flash, jsonify
from myapp.database import *
from functools import wraps
from sqlalchemy import text
import requests
import pandas as pd
import matplotlib.pyplot as plt
from myapp import socket

views = Blueprint('views', __name__, static_folder='static', template_folder='templates')


# Login decorator to ensure user is logged in before accessing certain routes
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("views.login"))
        return f(*args, **kwargs)

    return decorated


# Index route, this route redirects to login/register page
@views.route("/", methods=["GET", "POST"])
def index():
    """
    Redirects to the login/register page.

    Returns:
        Response: Flask response object.
    """
    return redirect(url_for("views.login"))


# Register a new user and hash password
import os
from werkzeug.utils import secure_filename

# Définir les extensions d'image autorisées
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Définir le chemin du répertoire pour stocker les images d'utilisateur
image_dir = os.path.join(os.getcwd(),  'myapp','static', 'images', 'users')  # Chemin absolu
if not os.path.exists(image_dir):
    os.makedirs(image_dir)

@views.route("/register", methods=["GET", "POST"])
def register():
    """
    Gère l'enregistrement de l'utilisateur, le hachage du mot de passe, et le téléchargement de l'image de profil.
    """
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        username = request.form["username"].strip().lower()
        password = request.form["password"]
        profile_image = request.files.get("profile_image")

        # Vérifier si l'utilisateur existe déjà
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("L'utilisateur existe déjà avec ce nom d'utilisateur.")
            return redirect(url_for("views.login"))

        # Gérer le téléchargement de l'image de profil
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            image_path = os.path.join(image_dir, filename)
            profile_image.save(image_path)
            image_url = os.path.join('static', 'images', 'users', filename)  # Enregistrer le chemin relatif dans la base de données
        else:
            flash("Veuillez télécharger un fichier image valide pour votre profil.")
            return redirect(url_for("views.register"))

        
        new_user = User(username=username, email=email, password=password, profile_image=image_url)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # Créer une nouvelle liste de chat pour l'utilisateur nouvellement enregistré
        new_chat = Chat(user_id=new_user.id, chat_list=[])
        db.session.add(new_chat)
        db.session.commit()

        flash("Enregistrement réussi.")
        return redirect(url_for("views.login"))

    return render_template("auth.html")
@views.route("/login", methods=["GET", "POST"])
def login():
    """
    Handles user login and session creation.

    Returns:
        Response: Flask response object.
    """
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        # Query the database for the inputted email address
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # Create a new session for the newly logged-in user
            session["user"] = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
            return redirect(url_for("views.chat"))
        else:
            flash("Invalid login credentials. Please try again.")
            return redirect(url_for("views.login"))

    return render_template("auth.html")


@views.route("/new-chat", methods=["POST"])
@login_required
def new_chat():
    """
    Creates a new chat room and adds users to the chat list based on username.

    Returns:
        Response: Flask response object.
    """
    user_id = session["user"]["id"]
    new_chat_username = request.form["username"].strip().lower()

    # If user is trying to add themselves, do nothing
    if new_chat_username == session["user"]["username"]:
        flash("You cannot create a chat with yourself.")
        return redirect(url_for("views.chat"))

    # Check if the recipient user exists
    recipient_user = User.query.filter_by(username=new_chat_username).first()
    if not recipient_user:
        flash("User with this username does not exist.")
        return redirect(url_for("views.chat"))

    # Check if the chat already exists
    existing_chat = Chat.query.filter_by(user_id=user_id).first()

    if not existing_chat:
        existing_chat = Chat(user_id=user_id, chat_list=[])
        db.session.add(existing_chat)
        db.session.commit()

    # Check if the new chat is already in the chat list
    if recipient_user.id not in [user_chat["user_id"] for user_chat in existing_chat.chat_list]:
        # Generate a room_id (you may use your logic to generate it)
        room_id = str(int(recipient_user.id) + int(user_id))[-4:]

        # Add the new chat to the chat list of the current user
        updated_chat_list = existing_chat.chat_list + [{"user_id": recipient_user.id, "room_id": room_id}]
        existing_chat.chat_list = updated_chat_list
        existing_chat.save_to_db()

        # Create a new chat list for the recipient user if it doesn't exist
        recipient_chat = Chat.query.filter_by(user_id=recipient_user.id).first()
        if not recipient_chat:
            recipient_chat = Chat(user_id=recipient_user.id, chat_list=[])
            db.session.add(recipient_chat)
            db.session.commit()

        # Add the new chat to the chat list of the recipient user
        updated_chat_list = recipient_chat.chat_list + [{"user_id": user_id, "room_id": room_id}]
        recipient_chat.chat_list = updated_chat_list
        recipient_chat.save_to_db()

        # Create a new message entry for the chat room
        new_message = Message(room_id=room_id)
        db.session.add(new_message)
        db.session.commit()

    return redirect(url_for("views.chat"))




# Login decorator to ensure user is logged in before accessing certain routes
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("views.login"))
        return f(*args, **kwargs)
    return decorated




@views.route('/get_name')
def get_name():
    """
    :return: json object with username
    """
    data = {'name': ''}
    if 'username' in session:
        data = {'name': session['username']}

    return jsonify(data)


@views.route('/get_messages')
def get_messages():
    """
    query the database for messages o in a particular room id
    :return: all messages
    """
    pass

from io import BytesIO


@views.route('/leave')
def leave():
    """
    Emits a 'disconnect' event and redirects to the home page.

    Returns:
        Response: Flask response object.
    """
    socket.emit('disconnect')
    return redirect(url_for('views.home'))



from io import BytesIO
import requests
from flask import send_file, redirect, url_for, flash, render_template, request, session
from datetime import datetime

# File.io API URL
FILE_IO_API_URL = "https://file.io"

def upload_file_to_fileio(file):
    """
    Upload a file to file.io and return the download URL and original filename.
    """
    response = requests.post(FILE_IO_API_URL, files={'file': file})
    if response.status_code == 200:
        response_data = response.json()
        file_url = response_data.get('link')
        original_filename = file.filename  # Retain the original filename
        return file_url, original_filename
    return None, None

def download_file_from_fileio(file_url):
    """
    Download a file from file.io and return it as a BytesIO object.
    """
    response = requests.get(file_url)
    if response.status_code == 200:
        return BytesIO(response.content)  # Return the file content as a BytesIO stream
    return None

@views.route("/chat/", methods=["GET", "POST"])
@login_required
def chat():
    """
    Renders the chat interface and displays chat messages, handles file uploads.
    """
    room_id = request.args.get("rid", None)
    current_user_id = session["user"]["id"]
    current_user_chats = Chat.query.filter_by(user_id=current_user_id).first()
    chat_list = current_user_chats.chat_list if current_user_chats else []

    # Initialize context that contains information about the chat room
    data = []

    for chat in chat_list:
        user = User.query.get(chat["user_id"])
        username = user.username
        profile_image = user.profile_image
        is_active = room_id == chat["room_id"]

        try:
            message = Message.query.filter_by(room_id=chat["room_id"]).first()
            last_message = message.messages[-1]
            last_message_content = last_message.content
        except (AttributeError, IndexError):
            last_message_content = "This place is empty. No messages ..."

        data.append({
            "username": username,
            "room_id": chat["room_id"],
            "is_active": is_active,
            "last_message": last_message_content,
            "profile_image": profile_image
        })

    # Handle file uploads
    if request.method == "POST":
        message_content = request.form["message"]
        file = request.files.get("file")

        if file:
            file_url, original_filename = upload_file_to_fileio(file)
            if file_url:
                # Save a link to the new route for downloading the file
                download_route = url_for("views.download_file", file_url=file_url, filename=original_filename)
                message_content = f"File uploaded: <a href='{download_route}' target='_blank'>Download {original_filename}</a>"

        if message_content:
            new_message = ChatMessage(
                content=message_content,
                sender_id=current_user_id,
                sender_username=session["user"]["username"],
                room_id=room_id,
                timestamp=str(datetime.utcnow())
            )
            new_message.save_to_db()

        return redirect(url_for("views.chat", rid=room_id))

    # Get all messages for the room
    messages = Message.query.filter_by(room_id=room_id).first().messages if room_id else []

    return render_template(
        "chat.html",
        user_data=session["user"],
        room_id=room_id,
        data=data,
        messages=messages,
    )



@views.route("/download_file", methods=["GET"])
def download_file():
    """
    Download a file from file.io and send it to the user.
    """
    file_url = request.args.get("file_url")
    filename = request.args.get("filename")  # Get the filename from the query string
    if not file_url or not filename:
        flash("File URL or filename is missing.", "error")
        return redirect(url_for("views.chat"))

    file_stream = download_file_from_fileio(file_url)
    if file_stream:
        # Send the file to the user for download with the original filename
        return send_file(file_stream, as_attachment=True, download_name=filename)
    flash("Failed to download the file.", "error")
    return redirect(url_for("views.chat"))







@views.app_template_filter("ftime")
def ftime(date):
    try:
        # Check if the date is already in datetime format
        if isinstance(date, str):
            # Parse the string to a datetime object
            dt = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
        else:
            # If date is a timestamp, convert it directly
            dt = datetime.fromtimestamp(int(date))

        # Format the datetime object
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except ValueError:
        return "Invalid date format"










































# def vigenere_cipher(text, key, mode='encrypt'):
#     result = []
#     key = [ord(i) for i in key]  # Convertir la clé en une liste de codes ASCII
#     text = [ord(i) for i in text]  # Convertir le texte en une liste de codes ASCII
#     key_index = 0

#     for char in text:
#         if mode == 'encrypt':
#             result.append(chr((char + key[key_index % len(key)]) % 256))
#         elif mode == 'decrypt':
#             result.append(chr((char - key[key_index % len(key)]) % 256))
        
#         key_index += 1

#     return ''.join(result)

# # Clé de chiffrement (à garder secrète)
# VIGENERE_KEY = "VIGENEREKEY123456"
