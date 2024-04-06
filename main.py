from flask import render_template, redirect, request, make_response, session
import flask
from data.user import User
from data.likes import Likes
from data.posts import Posts
from data.forms import LoginForm, RegisterForm, CommentForm
from data.comments import Comments
from data import db_session
from flask_login import LoginManager, login_user, login_required
from forms.news import NewsForm

db_session.global_init("db/sova.db")
db_sess = db_session.create_session()

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
current_user = None
userid = None
username = None

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():

    app.run(port=8080, host='127.0.0.1')


@app.route('/', methods=['GET', 'POST'])
def start():
    global current_user, userid, username
    mail, passw = session_get_user()
    user = 0
    if mail is not None and passw is not None:
        user = db_sess.query(User).filter(User.email == str(mail)).first()
    if user and user.check_password(passw):
        login_user(user)
        current_user = user
        username = user.name
        userid = user.id
    else:
        current_user = db_sess.query(User).filter(User.id == 1).first()
    userid = current_user.id
    username = current_user.name
    posts = db_sess.query(Posts).all()
    return render_template('start_page.html', typeuser=current_user.type_user,
                           link_user=f'/profile/{userid}/head',
                           username=username, news=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global current_user, username, userid
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == str(form.email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            current_user = user
            username = user.name
            userid = user.id
            set_session_user(form.email.data, user.hashed_password)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, typeuser=current_user.type_user, link_user=f'profile/{userid}',
                               username=username)
    return render_template('login.html', title='Авторизация', form=form, typeuser=current_user.type_user,
                           link_user=f'/profile/{userid}/head', username=username)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if db_sess.query(User).filter(User.email == str(form.email.data)).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        set_session_user(form.email.data, user.hashed_password)
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, typeuser=current_user.type_user,
                           link_user=f'/profile/{userid}', username=username)


@app.route('/profile/<id_user>/<mode>')
def page_of_user(id_user, mode):
    user = db_sess.query(User).filter(User.id == int(id_user)).first()
    post = db_sess.query(Posts).filter(Posts.user_id == int(id_user))
    if mode == 'head':
        return render_template('user.html', typeuser=current_user.type_user, link_user=f'/profile/{userid}/head',
                               username=user.name, post=post, another_typeuser=user.type_user)
    if mode == 'all_posts':
        return render_template('user_posts.html', typeuser=current_user.type_user, link_user=f'/profile/{userid}/head',
                               username=user.name, post=post)


@app.route('/add_news', methods=['GET', 'POST'])
@login_required
def add_news():
    global current_user
    form = NewsForm()
    if form.validate_on_submit():
        last_news = db_sess.query(Posts).count()
        news = Posts()
        news.title = form.title.data
        news.content = form.content.data
        news.user_link = f"/profile/{userid}/head"
        news.post_link = f"/posts/{last_news + 1}"
        news.likes = 0
        current_user.posts.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form, typeuser=current_user.type_user, link_user=f'/profile/{userid}/head',
                           username=username)


@app.route('/posts/<posts_id>', methods=['GET', 'POST'])
def news_more(posts_id):
    form = CommentForm()
    post = db_sess.query(Posts).filter(Posts.id == int(posts_id)).first()
    user = db_sess.query(User).filter(User.id == int(post.user_id)).first()
    if form.validate_on_submit():
        if form.like.data:
            like = Likes()
            like.post_id = post.id
            like.user_id = userid
            post.likes += 1
            db_sess.add(like)
            db_sess.commit()
        else:
            if form.comment.data != '':
                comment = Comments()
                comment.post_id = post.id
                comment.user_id = userid
                comment.text = form.comment.data
                db_sess.add(comment)
                db_sess.commit()
    comments = db_sess.query(Comments).filter(Comments.post_id == int(posts_id))
    return render_template('post.html', form=form, typeuser=current_user.type_user, link_user=f'/profile/{userid}/head',
                           username=username, user=user, post=post, comments=comments)


def session_get_user():
    email = session.get('email', 0)
    password = session.get('password', 0)
    return email, password


def set_session_user(email, passw):
    session["email"] = email
    session["password"] = passw


if __name__ == '__main__':
    main()
