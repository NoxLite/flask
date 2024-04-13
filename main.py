from flask import render_template, redirect, request, make_response, session
import flask
from data.user import User
from data.likes import Likes
from data.posts import Posts
from data.forms import LoginForm, RegisterForm, CommentForm, AddSong
from data.comments import Comments
from data.song import Song
from data import db_session
from flask_login import LoginManager, login_user, login_required
from forms.news import NewsForm
import datetime
from wtforms import SubmitField

db_session.global_init("db/sova.db")
db_sess = db_session.create_session()

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=365)
current_user = None
userid = None
username = None
login_manager = LoginManager()
login_manager.init_app(app)


def get_user_from_session():
    user = 0
    mail = session['email']
    passw = session['password']
    if mail is not None and passw is not None:
        user = db_sess.query(User).filter(User.email == str(mail)).first()
    if user and user.check_password(passw):
        login_user(user)
        current_user = user
    else:
        current_user = db_sess.query(User).filter(User.id == 1).first()
    userid = current_user.id
    username = current_user.name
    return current_user, userid, username


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


def main():
    app.run(port=5000, host='127.0.0.1', debug=True)


@app.route('/', methods=['GET', 'POST'])
def start():
    global current_user, userid, username
    current_user, userid, username = get_user_from_session()
    posts = db_sess.query(Posts).all()
    return render_template('start_page.html', typeuser=current_user.type_user,
                           link_user=f'/profile/{userid}/head',
                           username=username, news=posts, songs=get_song())


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
            session["email"] = form.email.data
            session["password"] = form.password.data
            session.modified = True
            session.permanent = True
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
    current_user, userid, username = get_user_from_session()
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
    current_user, userid, username = get_user_from_session()
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
    current_user, userid, username = get_user_from_session()
    form = CommentForm()
    post = db_sess.query(Posts).filter(Posts.id == int(posts_id)).first()
    user = db_sess.query(User).filter(User.id == int(post.user_id)).first()
    comments = db_sess.query(Comments).filter(Comments.post_id == int(posts_id))
    if db_sess.query(Likes).filter(Likes.user_id == current_user.id).first():
        form.like.label.text = 'Нравится'
    else:
        form.like.label.text = 'Понравилось'
    post.likes = len(list(db_sess.query(Likes)))

    if form.validate_on_submit():
        if form.like.data:
            if form.like.label.text == 'Понравилось':
                form.like.label.text = 'Нравится'
                like = Likes()
                like.post_id = post.id
                like.user_id = userid
                db_sess.add(like)
            else:
                form.like.label.text = 'Понравилось'
                like = db_sess.query(Likes).filter(Likes.user_id == current_user.id).first()
                db_sess.delete(like)
            db_sess.commit()
        else:
            if form.comment.data != '':
                comment = Comments()
                comment.post_id = post.id
                comment.user_id = userid
                comment.text = form.comment.data
                db_sess.add(comment)
                db_sess.commit()
    return render_template('post.html', form=form, typeuser=current_user.type_user, link_user=f'/profile/{userid}/head',
                username=username, user=user, post=post, comments=comments)


@app.route('/song/<song_id>')
def song(song_id):
    current_user, userid, username = get_user_from_session()
    song = db_sess.query(Song).filter(Song.id == int(song_id)).first()
    author = db_sess.query(User).filter(User.id == int(song.user_id)).first()
    return render_template('song.html', typeuser=current_user.type_user, link_user=f'/profile/{userid}/head',
                           username=username, song=song, author=author.name)


@app.route('/add_song', methods=['GET', 'POST'])
@login_required
def add_song():
    current_user, userid, username = get_user_from_session()
    form = AddSong()
    img = r'/static/inf/covers/classic.png'
    id_s = len(list(db_sess.query(Song).filter(Song.user_id == current_user.id))) + 1
    if request.method == 'POST':
        if form.update.data:
            f = request.files['file']
            with open(f'static/inf/covers/{current_user.id}_{id_s}_song.png', 'wb') as image:
                image.write(f.read())
            img = f'/static/inf/covers/{current_user.id}_{id_s}_song.png'
        elif form.public.data:
            if form.title.data != '':
                song = Song()
                song.title = form.title.data
                song.user_id = current_user.id
                song.user_link = f'/profile/{current_user.id}/head'
                song.cover = img
                song.likes = 0
                db_sess.add(song)
                db_sess.commit()
                return redirect(f'/')
    return render_template('add_song.html', typeuser=current_user.type_user, link_user=f'/profile/{userid}/head',
                           username=username, form=form, imag=img)


def get_song():
    song = list(db_sess.query(Song))[:4]
    return song


if __name__ == '__main__':
    main()
