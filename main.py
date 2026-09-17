from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lol'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите в систему'
login_manager.login_message_category = 'warning'



class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(200), nullable=True)
    text = db.Column(db.Text, nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users, int(user_id))



@app.route('/')
@login_required
def index():
    cards = Card.query.all()
    return render_template('index.html', cards=cards)


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Заполните все поля', 'danger')
            return redirect(url_for('register'))

        if Users.query.filter_by(username=username).first():
            flash('Пользователь уже существует', 'danger')
            return redirect(url_for('register'))

        new_user = Users(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация успешна! Войдите.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login/', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = Users.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Добро пожаловать, {user.username}!', 'success')
            return redirect(url_for('index'))

        flash('Неверный логин или пароль', 'danger')

    return render_template('login.html')


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'success')
    return redirect(url_for('home'))


@app.route('/card/<int:id>')
@login_required
def card(id):
    card_item = db.session.get(Card, id)
    if not card_item:
        flash('Карточка не найдена', 'danger')
        return redirect(url_for('index'))
    return render_template('card.html', card=card_item)


@app.route('/create')
@login_required
def create():
    return render_template('create.html')


@app.route('/form_create', methods=['GET', 'POST'])
@login_required
def form_create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        subtitle = request.form.get('subtitle', '').strip()
        text = request.form.get('text', '').strip()

        if not title or not text:
            flash('Заполните заголовок и текст', 'danger')
            return redirect(url_for('create'))

        new_card = Card(title=title, subtitle=subtitle, text=text)
        db.session.add(new_card)
        db.session.commit()

        flash('Карточка создана!', 'success')
        return redirect(url_for('index'))

    return redirect(url_for('create'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)