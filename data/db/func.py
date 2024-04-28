from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_, desc
import jwt
from data.db.users import User
from data.db.notes import Note
from data.custom_exceptions import *
from data.configs import *
import re
import datetime


def register_user(session, username, password):
    if (username is None) or (password is None):
        raise NoneCredentialsError("Username or password are required")

    if not is_username_correct(username):
        raise InvalidUsernameError("Username is invalid")

    if not is_password_correct(password):
        raise InvalidPasswordError("Password is invalid")

    if is_user_exists(session, username):
        raise UserAlreadyExistsError("User already exists")

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, password_hash=hashed_password)
    session.add(new_user)
    session.commit()

    return {
        "message": "User successfully registered",
        "status": True
    }


def login_user(session, username, password):
    if (username is None) or (password is None):
        raise NoneCredentialsError()

    if not is_user_exists(session, username):
        raise UserDoesNotExistsError()

    validation_res = is_password_matched(session, username, password)
    if not validation_res:
        raise IncorrectPasswordError()

    token = jwt.encode({
        'user_id': validation_res,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm='HS256')

    return {
        "message": "Login successful",
        "token": token,
        "status": True
    }


def create_note(session, user_id, title, text):
    if (not title) or (not text):
        raise NoneNoteParamsError()

    if len(title) > MAX_TITLE_LENGTH:
        raise InvalidTitleError("Title is too long.")

    if len(text) > MAX_TEXT_LENGTH:
        raise InvalidTextError("Text is too long.")

    new_note = Note(user_id=user_id, title=title, text=text)
    session.add(new_note)
    session.commit()

    return {
        "message": "Note created successfully",
        "note_id": new_note.id,
        "title": new_note.title,
        "text": new_note.text,
        "status": True
    }


def edit_note(session, note_id, title, text, token):
    note = session.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise NoteDoesNotExistsError()

    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    if not (note.user_id == data['user_id']):
        raise AccessDeniedError()

    if not (datetime.datetime.now() - note.updated_date) > datetime.timedelta(days=1):
        raise OutdatedNoteError()

    if not title and not text:
        raise NoneNoteParamsError()

    if not title:
        new_title = note.title
    else:
        new_title = title
    if not text:
        new_text = note.text
    else:
        new_text = text

    session.query(Note).filter(Note.id == note_id).update({
        Note.title: new_title,
        Note.text: new_text
    })
    session.commit()

    return {
        "message": "Note edited successfully",
        "note_id": note.id,
        "title": note.title,
        "text": note.text,
        "status": True
    }


def delete_note(session, note_id, token):
    note = session.query(Note).filter(Note.id == note_id).first()

    if not note:
        raise NoteDoesNotExistsError()

    data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

    if not (note.user_id == data['user_id']):
        raise AccessDeniedError()

    session.delete(note)
    session.commit()

    return {
        "message": "Note deleted successfully",
        "note_id": note.id,
        "title": note.title,
        "text": note.text,
        "status": True
    }


def show_notes(session, start_date, end_date, page, per_page, user_id, token):
    if not page:
        page = DEFAULT_PAGE
    if not per_page:
        per_page = DEFAULT_PER_PAGE

    conditions = []

    if page < 1 or per_page < 1:
        raise InvalidPageParamsError

    start_index = (page - 1) * per_page

    if start_date and end_date and start_date > end_date:
        raise InvalidDateGapError()

    if start_date and is_valid_date_format(start_date):
        conditions.append(Note.created_date >= start_date)
    if end_date and is_valid_date_format(end_date):
        conditions.append(Note.created_date <= end_date)
    if user_id:
        conditions.append(Note.user_id == user_id)

    if conditions:
        result = session.query(Note).filter(or_(*conditions))  ######check
    else:
        result = session.query(Note)

    if start_index >= result.count():
        raise ThereIsNoData()

    notes_query = result.order_by(desc(Note.created_date))
    total_notes = notes_query.count()
    notes = notes_query.offset(start_index).limit(per_page).all()

    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.exceptions.InvalidSignatureError as e:
        data = None

    notes_data = [{
        'id': note.id,
        'title': note.title,
        'text': note.text,
        'user_id': note.user_id,
        'created_at': note.created_date.isoformat(),
        'is_you_owner': ((note.user_id == data['user_id']) if data else False)
    } for note in notes]

    return {
        'notes': notes_data,
        'total': total_notes,
        'page': page,
        'per_page': per_page
    }


# ----------------------------------------------------------------------------------------------------------------------
def is_user_exists(session, username):
    exists = session.query(User.username).filter_by(username=username).first() is not None
    return exists


def is_password_matched(session, username, password):
    user = session.query(User).filter_by(username=username).first()

    if not check_password_hash(user.password_hash, password):
        return False

    return user.id


def is_username_correct(username):
    if not username:
        return False
    if (len(username) < MIN_PASSWORD_LENGTH) or (len(username) > MAX_PASSWORD_LENGTH):
        return False
    if not re.match("^[a-zA-Z0-9_.-]+$", username):
        return False
    return True


def is_password_correct(password):
    if not password:
        return False
    if len(password) < MIN_PASSWORD_LENGTH:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


def is_valid_date_format(date_string):
    pattern = r'^\d{4}\.\d{2}\.\d{2}$'
    return bool(re.match(pattern, date_string))
