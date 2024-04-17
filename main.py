from flask import render_template, redirect, request, make_response, session, jsonify
import flask
from data.user import User
from data.likes import Likes
from data.posts import Posts
from data.genres import Genre
from data.forms import LoginForm, RegisterForm, CommentForm, AddSong
from data.comments import Comments
from data.song import Song
from data import db_session
from flask_login import LoginManager, login_user, login_required, logout_user
from forms.news import NewsForm
import datetime, os
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
img = None
img_ava = None

def get_user_from_session():
    try:
        user = 0
        mail = session['email']
        passw = session['password']
        if mail is not None and passw is not None:
            user = db_sess.query(User).filter(User.email == str(mail)).first()
        if user and user.check_password(passw):
            login_user(user)
            current_user = user
            userid = current_user.id
            username = current_user.name
            return current_user, userid, username
    except Exception:
        return None, None, None
    return None, None, None


@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('email', None)
    session.pop('password', None)
    return redirect("/")


def main():
    app.run(port=5000, host='127.0.0.1', debug=True)


@app.route('/', methods=['GET', 'POST'])
def start():
    global current_user, userid, username
    current_user, userid, username = get_user_from_session()
    return render_template('start_page.html', current_user=current_user, news=get_post(), songs=get_song(),
                           get_aut=get_author, redirect_song=redirect_song)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global current_user, username, userid
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == str(form.email.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user)
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
    return render_template('login.html', title='Авторизация', form=form)

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
        if form.about.data != '':
            user.about = form.about.data
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/profile/<id_user>/<mode>', methods=['GET', 'POST'])
def page_of_user(id_user, mode):
    global img_ava
    current_user, userid, username = get_user_from_session()
    user = db_sess.query(User).filter(User.id == int(id_user)).first()
    post = db_sess.query(Posts).filter(Posts.user_id == int(id_user))
    try:
        taste = list(map(int, user.genres.split(';')))
    except Exception:
        taste = []
    if mode == 'head':
        return render_template('user.html', current_user=current_user, link_user=f'/profile/{userid}/head',
                               user=user, post=post)
    if mode == 'all_posts':
        return render_template('user_posts.html', current_user=current_user, post=post)
    if mode == 'change-image' and current_user.id == user.id:
        form = AddSong()
        if not img_ava:
            img_ava = '/static/inf/avatars/classic_avatar.png'
        if request.method == 'POST':
            if form.public.data:
                with open(f'static/inf/avatars/{id_user}_prom.png', 'rb') as f:
                    with open(f'static/inf/avatars/{id_user}.png', 'wb') as n:
                        n.write(f.read())
                os.remove(f'static/inf/avatars/{id_user}_prom.png')
                img_ava = f'/static/inf/avatars/{id_user}.png'
                user.avatar = img_ava
                db_sess.commit()
                img_ava = None
                return redirect(f'/profile/{id_user}/head')
            if form.update.data:
                with open(f'static/inf/avatars/{id_user}_prom.png', 'wb') as f:
                    f.write(request.files['file'].read())
                img_ava = f'/static/inf/avatars/{id_user}_prom.png'
        return render_template('change_avatar.html', current_user=current_user, img=img_ava, form=form)
    elif mode == 'change-genres' and current_user.id == user.id:
        genres = db_sess.query(Genre).all()
        form = AddSong()
        if form.public.data:
            for elem in request.form.lists():
                if 'genre' in elem:
                    taste = elem[1]
                    user.genres = ';'.join(taste)
                    db_sess.commit()
            taste = list(map(int, taste))
            return redirect(f'/profile/{id_user}/head')
        return render_template('change_genres.html', genres=genres, form=form, taste=taste)
    else:
        return redirect(f'/profile/{id_user}/head')


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
        news.post_link = f"/posts/{last_news + 1}/head"
        news.likes = 0
        current_user.posts.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', title='Добавление новости',
                           form=form, current_user=current_user)


@app.route('/posts/<posts_id>/<type>', methods=['GET', 'POST'])
def news_more(posts_id, type):
    current_user, userid, username = get_user_from_session()
    form = CommentForm()
    post = db_sess.query(Posts).filter(Posts.id == int(posts_id)).first()
    user = db_sess.query(User).filter(User.id == int(post.user_id)).first()
    comments = db_sess.query(Comments).filter(Comments.post_id == int(posts_id))
    if type == 'head':
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

    if type == 'comment':
        if request.method == 'POST':
            if form.comment.data != '':
                comment = Comments()
                comment.post_id = post.id
                comment.user_id = userid
                comment.text = form.comment.data
                db_sess.add(comment)
                db_sess.commit()
                return redirect(f'/posts/{posts_id}/head')
        else:
            return render_template('comment_post.html', form=form, current_user=current_user)
    return render_template('post.html', form=form, current_user=current_user, user=user, post=post,
                           comments=comments, get_author=get_author, get_avatar=get_avatar)


@app.route('/song/<song_id>')
def song(song_id):
    current_user, userid, username = get_user_from_session()
    song = db_sess.query(Song).filter(Song.id == int(song_id)).first()
    author = db_sess.query(User).filter(User.id == int(song.user_id)).first()
    genres = db_sess.query(Genre)
    return render_template('song.html', current_user=current_user, song=song, author=author.name, get_genre_name=get_genre_name)


@app.route('/add_song', methods=['GET', 'POST'])
@login_required
def add_song(genre=1):
    global img
    current_user, userid, username = get_user_from_session()
    form = AddSong()
    genres = db_sess.query(Genre)
    if not img:
        img = r'/static/inf/covers/classic.png'
    id_s = len(list(db_sess.query(Song).filter(Song.user_id == current_user.id))) + 1
    if request.method == 'POST':
        if form.update.data:
            f = request.files['file']
            with open(f'static/inf/covers/{current_user.id}_{id_s}_song.png', 'wb') as image:
                image.write(f.read())
            img = f'/static/inf/covers/{current_user.id}_{id_s}_song.png'
            genre = int(request.form.get('genre'))
        elif form.public.data:
            if form.title.data != '':
                song = Song()
                song.genre = int(request.form.get('genre'))
                song.title = form.title.data
                song.user_id = current_user.id
                song.user_link = f'/profile/{current_user.id}/head'
                song.cover = img
                song.likes = 0
                db_sess.add(song)
                db_sess.commit()
                img = None
                return redirect(f'/')
    return render_template('add_song.html', current_user=current_user, form=form, imag=img, genres=genres, choosed=genre)


def get_song():
    song = list(db_sess.query(Song))[-4:]
    return song


@app.route('/my_profile')
def redirect_my_profile():
    link = f'/profile/{current_user.id}/head'
    return redirect(link)


def get_post():
    post = list(db_sess.query(Posts))[:-5:-1]
    return post


def get_author(id):
    user = db_sess.query(User).filter(User.id == int(id)).first()
    return user.name


def get_avatar(id):
    user = db_sess.query(User).filter(User.id == int(id)).first()
    return user.avatar


@app.route("/redirect-song/<songid>")
def redirect_song(songid):
    return redirect(f'/song/{songid}')


@app.errorhandler(404)
def not_found(error):
    return render_template('error404.html')


def get_genre_name(id_genre):
    genre = db_sess.query(Genre).filter(Genre.id == id_genre).first()
    return genre.name

if __name__ == '__main__':
    main()
