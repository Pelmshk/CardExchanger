import datetime
import os

from flask import Flask, render_template, redirect, request, abort
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from werkzeug.utils import secure_filename

from data import db_session
from data.announces import Announces
from data.users import User
from forms.user import LoginForm, RegisterForm, EditForm

UPLOAD_FOLDER = 'C:/Users/Po_iv/PycharmProjects/CardChanger/static/pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)


def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


def main():
    db_session.global_init("db/card_changer.db")
    app.run(port=8080, host='127.0.0.1')


@app.route("/")
def index():
    db_sess = db_session.create_session()
    announces = db_sess.query(Announces).all()[::-1]
    images_path = []
    for i in announces:
        images_path.append(f'static/pics/{i.image}')
    return render_template("index.html", announces=announces, images_path=images_path, len=len(announces))


@app.route("/user_announces")
@login_required
def user_announces():
    db_sess = db_session.create_session()
    announces = db_sess.query(Announces).join(Announces.user).filter(User.id == current_user.id)[::-1]
    images_path = []
    for i in announces:
        images_path.append(f'static/pics/{i.image}')
    return render_template("User_anns.html", announces=announces, images_path=images_path, len=len(images_path),
                           current_user=current_user)


@app.route("/user_address_anns")
@login_required
def user_address_anns():
    db_sess = db_session.create_session()
    announces = db_sess.query(Announces).join(Announces.user).filter(User.address == current_user.address)[::-1]
    images_path = []
    for i in announces:
        images_path.append(f'static/pics/{i.image}')
    return render_template("index.html", announces=announces, images_path=images_path, len=len(images_path))



@app.route("/claim/<int:id>")
@login_required
def claim(id):
    db_sess = db_session.create_session()
    ann = db_sess.query(Announces).filter(Announces.id == id).first()
    ann.claim = True
    db_sess.commit()
    return redirect("/")


@app.route("/reject_claim/<int:id>")
@login_required
def reject(id):
    db_sess = db_session.create_session()
    ann = db_sess.query(Announces).filter(Announces.id == id).first()
    ann.claim = False
    db_sess.commit()
    return redirect("/claims")


@app.route("/claims")
@login_required
def claims():
    db_sess = db_session.create_session()
    announces = db_sess.query(Announces).filter(Announces.claim == 1)[::-1]
    images_path = []
    for i in announces:
        images_path.append(f'static/pics/{i.image}')
    return render_template("claims.html", announces=announces, images_path=images_path, len=len(images_path))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template("register.html", title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title="Регистрация", form=form)


@app.route('/new_announce', methods=['GET', 'POST'])
@login_required
def new_announce():
    db_sess = db_session.create_session()
    if request.method == 'POST':
        new_announce = Announces(
            title=request.form['title'],
            fandom=request.form['fandom'],
            exchange=request.form['exchange'],
            cost=request.form['cost'],
            content=request.form['content'],
            user_id=current_user.id
        )
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_announce.image = filename
        db_sess.add(new_announce)
        db_sess.commit()
        return redirect('/')
    return render_template('new_announce.html', title='Создать новое объявление')


@app.route('/ann_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def ann_delete(id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Announces).filter(Announces.id == id).first()
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/user_announces')


@app.route('/ann_delete_cl/<int:id>', methods=['GET', 'POST'])
@login_required
def ann_delete_cl(id):
    db_sess = db_session.create_session()
    jobs = db_sess.query(Announces).filter(Announces.id == id).first()
    if jobs:
        db_sess.delete(jobs)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/claims')


@app.route('/edit_user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    form = EditForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        users = db_sess.query(User).filter(User.id == id).first()
        if users:
            form.surname.data = users.surname
            form.name.data = users.name
            form.phone.data = users.phone
            form.address.data = users.address
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        users = db_sess.query(User).filter(User.id == id).first()
        if users:
            users.surname = form.surname.data
            users.name = form.name.data
            users.phone = form.phone.data
            users.address = form.address.data
            db_sess.commit()
            return redirect('/user_announces')
        else:
            abort(404)
    return render_template('edit_user.html',
                           title='Изменить профиль',
                           form=form)


if __name__ == '__main__':
    main()
