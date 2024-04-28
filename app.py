from flask import Flask, request, jsonify
from data.db.users import User
from data.db.func import register_user, login_user, create_note, edit_note, delete_note, show_notes
from data.db.db_session import global_init, create_session
from data.custom_exceptions import ValidationError
from data.configs import SECRET_KEY
import jwt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/databasename'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

global_init()
db_sess = create_session()
print(0)


def token_required(f):
    """
        Декоратор для верификации JWT токена, полученного в заголовках запроса.
        Использует глобальную переменную SECRET_KEY для декодирования токена.
        Проверяет, что токен существует, и что он валиден.
        Если проверка проходит успешно, запрос передается в оригинальную функцию с
        добавлением объекта current_user как первого аргумента.

        Args:
            f (function): Функция, к которой будет применен декоратор.

        Returns:
            function: Обернутая функция с проверкой токена.

        Raises:
            403: Ошибка возникает, если токен отсутствует в заголовках запроса.
            401: Ошибка возникает, если токен невалиден, или если пользователь не найден.
        """

    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = db_sess.query(User).get(data['user_id'])
            if not current_user:
                return jsonify({'message': 'Invalid token!'}), 401
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    decorated.__name__ = f.__name__
    return decorated


@app.route('/register', methods=['POST'])
def register():
    """
        Обрабатывает запрос на регистрацию нового пользователя. Ожидает получение JSON объекта с
        именем пользователя и паролем. После получения вызывает функцию register_user для
        регистрации пользователя в системе.

        Пример тела запроса:
        {
            "username": "newuser",
            "password": "newpassword123"
        }

        Returns:
            JSON response: Возвращает JSON с сообщением о результате регистрации.
            HTTP status code: Возвращает код состояния HTTP в зависимости от результата операции.
                201 - если регистрация прошла успешно.
                400 - если данные некорректны (обрабатывается ValidationError).
                500 - в случае других ошибок сервера.

        Raises:
            ValidationError: Возникает, когда введены некорректные данные пользователя.
            Exception: Ловит неспецифицированные исключения, указывающие на проблемы в работе сервера.
        """
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        result = register_user(db_sess, username, password)
        return jsonify({"message": result['message']}), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"message": "Internal server error"}), 500


@app.route('/login', methods=['POST'])
def login():
    """
        Обрабатывает запрос на аутентификацию пользователя. Ожидает получение JSON объекта с
        именем пользователя и паролем. Вызывает функцию login_user для проверки учетных данных
        и генерации токена JWT, если данные верны.

        Пример тела запроса:
        {
            "username": "existinguser",
            "password": "userpassword"
        }

        Returns:
            JSON response: Возвращает JSON с результатом аутентификации, включая JWT токен,
            если аутентификация прошла успешно.
            HTTP status code:
                200 - если аутентификация прошла успешно.
                400 - если данные некорректны (обрабатывается ValidationError).
                500 - в случае других ошибок сервера.

        Raises:
            ValidationError: Возникает, когда предоставлены неверные учетные данные.
            Exception: Ловит неспецифицированные исключения, указывающие на проблемы в работе сервера.
        """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    try:
        result = login_user(db_sess, username, password)
        return jsonify(result), 200
    except ValidationError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"message": "Internal server error"}), 500


@app.route('/create_note', methods=['POST'])
@token_required
def add_note(current_user):
    """
        Обрабатывает POST запрос для создания новой заметки. Этот метод требует аутентификации.
        Ожидает получение JSON объекта с заголовком и текстом заметки. После проверки входных данных
        и аутентификации пользователя функция create_note создает новую заметку в базе данных.

        Пример тела запроса:
        {
            "title": "New Note Title",
            "text": "Details of the new note."
        }

        Args:
            current_user (User): Аутентифицированный пользователь, извлекается из декодированного JWT токена.

        Returns:
            JSON response: Возвращает JSON с сообщением о создании заметки и ее параметрами.
            HTTP status code:
                201 - если заметка успешно создана.
                400 - если данные некорректны (обрабатывается ValidationError).
                500 - в случае других ошибок сервера.

        Raises:
            ValidationError: Возникает, когда введенные данные не проходят валидацию (например, слишком длинное название).
            Exception: Ловит неспецифицированные исключения, указывающие на внутренние проблемы сервера.
        """
    title = request.json.get('title')
    text = request.json.get('text')
    try:
        result = create_note(db_sess, current_user.id, title, text)
        return jsonify(result), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"message": "Internal server error"}), 500


@app.route('/edit_note', methods=['POST'])
@token_required
def edit_notes(current_user):
    """
        Обрабатывает POST запрос на редактирование существующей заметки. Этот метод требует аутентификации.
        Ожидает получение JSON объекта с идентификатором заметки, новым заголовком и новым текстом заметки.
        Проверяет, что пользователь имеет права на редактирование этой заметки, а также проверяет валидность новых данных.

        Пример тела запроса:
        {
            "note_id": 1,
            "new_title": "Updated Note Title",
            "new_text": "Updated details of the note."
        }

        Args:
            current_user (User): Аутентифицированный пользователь, извлекается из декодированного JWT токена.

        Returns:
            JSON response: Возвращает JSON с обновлённой информацией о заметке.
            HTTP status code:
                201 - если заметка успешно обновлена.
                400 - если данные некорректны (обрабатывается ValidationError).
                500 - в случае других ошибок сервера.

        Raises:
            ValidationError: Возникает, когда введенные данные не проходят валидацию или когда отсутствует право на редактирование заметки.
            Exception: Ловит неспецифицированные исключения, указывающие на внутренние проблемы сервера.
        """
    note_id = request.json.get('note_id')
    new_title = request.json.get('new_title')
    new_text = request.json.get('new_text')
    token = request.headers.get('Authorization')
    try:
        result = edit_note(db_sess, note_id, new_title, new_text, token)
        return jsonify(result), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"message": "Internal server error"}), 500


@app.route('/delete_note', methods=['POST'])
@token_required
def delete_notes(current_user):
    """
        Обрабатывает POST запрос на удаление заметки. Этот метод требует аутентификации.
        Ожидает получение JSON объекта с идентификатором заметки для удаления.
        Проверяет, что пользователь имеет права на удаление этой заметки.

        Пример тела запроса:
        {
            "note_id": 1
        }

        Args:
            current_user (User): Аутентифицированный пользователь, извлекается из декодированного JWT токена.

        Returns:
            JSON response: Возвращает JSON с сообщением о результате удаления заметки.
            HTTP status code:
                201 - если заметка успешно удалена.
                400 - если данные некорректны (обрабатывается ValidationError).
                500 - в случае других ошибок сервера.

        Raises:
            ValidationError: Возникает, когда отсутствует право на удаление заметки или заметка не найдена.
            Exception: Ловит неспецифицированные исключения, указывающие на внутренние проблемы сервера.
        """
    note_id = request.json.get('note_id')
    token = request.headers.get('Authorization')
    try:
        result = delete_note(db_sess, note_id, token)
        return jsonify(result), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"message": "Internal server error"}), 500


@app.route('/show_notes', methods=['POST'])
def get_notes():
    """
    Обрабатывает POST запрос на получение списка заметок с фильтрацией и пагинацией. Этот метод требует аутентификации.
    Ожидает получение данных в формате JSON, включая параметры страницы, количество элементов на странице,
    начальную и конечную даты фильтрации и идентификатор пользователя.

    Пример тела запроса:
    {
        "page": 1,
        "per_page": 10,
        "start_date": "2022-01-01",
        "end_date": "2022-01-31",
        "user_id": 2
    }

    API Args:
        page (int): Номер страницы для пагинации.
        per_page (int): Количество заметок на одной странице.
        start_date (str): Начальная дата для фильтрации заметок.
        end_date (str): Конечная дата для фильтрации заметок.
        user_id (int): Идентификатор пользователя для фильтрации заметок.

    Returns:
        JSON response: JSON с данными о заметках и информацией о пагинации.
        HTTP status code:
            201 - если запрос выполнен успешно.
            400 - если данные некорректны или не проходят валидацию.
            500 - в случае внутренних ошибок сервера.

    Raises:
        ValidationError: Генерируется, если переданы некорректные данные.
        Exception: Отлавливает неспецифицированные исключения, указывающие на другие проблемы.
    """
    page = request.json.get('page')
    per_page = request.json.get('per_page')
    start_date = request.json.get('start_date')
    end_date = request.json.get('start_date')
    user_id = request.json.get('user_id')

    token = request.headers.get('Authorization')

    try:
        result = show_notes(db_sess, start_date, end_date, page, per_page, user_id, token)
        return jsonify(result), 201
    except ValidationError as e:
        return jsonify({"error": str(e)}), e.status_code
    except Exception as e:
        return jsonify({"message": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=True)
