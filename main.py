"""Форум для обсуждения музыки(основной код)"""

import datetime
import os
import requests
import flask
from flask import render_template, redirect, request, session, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user

from data import db_session
from data.comments import Comments
from data.comments_song import CommentsSong
from data.forms import LoginForm, RegisterForm, CommentForm, AddSong, SetEvent
from data.genres import Genre
from data.likes import Likes
from data.posts import Posts
from data.song import Song
from data.user import User
from data.events import Events
from data.news import NewsForm

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
API = '40d1649f-0493-4b70-98ba-98533de7710b'  # API Яндекс.Карт
map_file = '/static/inf/buttons/base_map.png'


# Получения логина и пароля пользователя из сессии
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


# Функция загрузки пользователя
@login_manager.user_loader
def load_user(user_id):
    return db_sess.query(User).get(user_id)


# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('email', None)
    session.pop('password', None)
    return redirect("/")


def main():
    app.run(port=5000, host='127.0.0.1')


# Стартовая страница
@app.route('/', methods=['GET', 'POST'])
def start():
    global current_user, userid, username
    current_user, userid, username = get_user_from_session()

    concerts = list(db_sess.query(Events).filter(Events.date >= datetime.datetime(
        datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day,
        datetime.datetime.now().hour, datetime.datetime.now().minute)))
    return render_template('start_page.html', current_user=current_user, news=get_post(), songs=get_song(),
                           get_aut=get_author, redirect_song=redirect_song, get_song_from_genre=get_song_from_genre,
                           len=len, concerts=concerts, title='Главная страница')


#  Страница регистрации
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


#  Страница регистрации
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


#  Страница пользователя
@app.route('/profile/<id_user>/<mode>', methods=['GET', 'POST'])
def page_of_user(id_user, mode):
    global img_ava
    current_user, userid, username = get_user_from_session()
    if current_user:
        user = db_sess.query(User).filter(User.id == int(id_user)).first()
        post = db_sess.query(Posts).filter(Posts.user_id == int(id_user))
        song = db_sess.query(Song).filter(Song.user_id == int(id_user))
        event = db_sess.query(Events).filter(Events.date >= datetime.datetime(
            datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day,
            datetime.datetime.now().hour, datetime.datetime.now().minute)).filter(Events.id == int(id_user))
        try:
            taste = list(map(int, user.genres.split(';')))
        except Exception:
            taste = []
        if mode == 'head':
            return render_template('user.html', current_user=current_user, link_user=f'/profile/{userid}/head',
                                   user=user, post=post, song=song, get_author=get_author, event=event,
                                   title=f"Страница {user.name}")
        if mode == 'all_songs':
            return render_template('all_songs.html', current_user=current_user, song=song, title='Все песни')
        if mode == 'all_events':
            return render_template('all_events.html', current_user=current_user, event=event, title="Все мероприятия")
        if mode == 'all_posts':
            return render_template('user_posts.html', current_user=current_user, post=post, title='Все посты')
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
            return render_template('change_avatar.html', current_user=current_user, img=img_ava, form=form,
                                   title='Изменить изображение профиля')
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
            return render_template('change_genres.html',
                                   genres=genres, form=form, taste=taste, title='Изменить предпочтения')
        else:
            return redirect(f'/profile/{id_user}/head')
    else:
        return redirect('/')


#  Страница добавления пользователя
@app.route('/add_news', methods=['GET', 'POST'])
@login_required
def add_news():
    current_user, userid, username = get_user_from_session()
    if current_user:
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
    else:
        return redirect('/')


#  Страница новости
@app.route('/posts/<posts_id>/<type>', methods=['GET', 'POST'])
def news_more(posts_id, type):
    current_user, userid, username = get_user_from_session()
    if current_user:
        form = CommentForm()
        post = db_sess.query(Posts).filter(Posts.id == int(posts_id)).first()
        user = db_sess.query(User).filter(User.id == int(post.user_id)).first()
        comments = db_sess.query(Comments).filter(Comments.post_id == int(posts_id))
        like = db_sess.query(Likes).filter(Likes.user_id
                                           == int(current_user.id)).filter(Likes.post_id == int(posts_id)).first()
        if like:
            print(like.id)
            liketext = 'Нравится ✅'
        else:
            liketext = 'Нравится'
        if type == 'head':
            post.likes = len(list(db_sess.query(Likes).filter(Likes.post_id == int(post.id))))
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
                return render_template('comment_post.html', form=form, current_user=current_user,
                                       title='Добавить комментарий')
        if type == 'like':
            like = db_sess.query(Likes).filter(Likes.user_id == int(current_user.id)).first()
            if like:
                db_sess.delete(like)
            else:
                like = Likes()
                like.user_id = current_user.id
                like.post_id = posts_id
                db_sess.add(like)
            db_sess.commit()
            return redirect(f'/posts/{posts_id}/head')
        if type == 'delete':
            if current_user == post.user_id:
                db_sess.delete(post)
                for elem in comments:
                    db_sess.delete(elem)
                for elem in db_sess.query(Likes).filter(Likes.post_id == int(post.id)):
                    db_sess.delete(elem)
                db_sess.commit()
            return redirect('/')
        return render_template('post.html', form=form, current_user=current_user, user=user, post=post,
                               comments=comments, get_author=get_author, get_avatar=get_avatar, liketext=liketext,
                               title=post.title)
    else:
        return redirect('/')


#  Страница песни
@app.route('/song/<song_id>/<type>', methods=['GET', 'POST'])
def song(song_id, type):
    current_user, userid, username = get_user_from_session()
    if current_user:
        song_data = db_sess.query(Song).filter(Song.id == int(song_id)).first()
        author = db_sess.query(User).filter(User.id == int(song_data.user_id)).first()
        comments = db_sess.query(CommentsSong).filter(CommentsSong.song_id == int(song_id))
        form = CommentForm()
        if type == 'head':
            pass
        if type == 'comment':
            if request.method == 'POST':
                if form.comment.data != '':
                    comment = CommentsSong()
                    comment.song_id = song_data.id
                    comment.user_id = userid
                    comment.text = form.comment.data
                    db_sess.add(comment)
                    db_sess.commit()
                    return redirect(f'/song/{song_id}/head')
            return render_template('comment_post.html', form=form, current_user=current_user)
        return render_template('song.html', current_user=current_user, song=song_data, author=author.name,
                               get_genre_name=get_genre_name, comments=comments, get_avatar=get_avatar,
                               get_author=get_author, title=song_data.title)
    else:
        return redirect('/')


#  Страница добавления песни
@app.route('/add_song', methods=['GET', 'POST'])
@login_required
def add_song(genre=1):
    global img
    current_user, userid, username = get_user_from_session()
    if current_user:
        form = AddSong()
        genres = db_sess.query(Genre)
        if not img:
            img = r'/static/inf/covers/classic.png'
        id_s = len(list(db_sess.query(Song).filter(Song.user_id == int(current_user.id)))) + 1
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
                    if form.link_spotify.data != '':
                        song.link_spotify = form.link_spotify.data
                    if form.link_yandex.data != '':
                        song.link_yandex = form.link_yandex.data
                    if form.link_youtube.data != '':
                        song.link_youtube = form.link_youtube.data
                    db_sess.add(song)
                    db_sess.commit()
                    img = None
                    return redirect(f'/')
        return render_template('add_song.html', current_user=current_user, form=form, imag=img, genres=genres,
                               choosed=genre, title='Добавить новую песню')
    else:
        return redirect('/')


#  Получение последних песен из БД
def get_song():
    song = list(db_sess.query(Song))[:-5:-1]
    return song


#  Переадресация на страницу текущего пользователя
@app.route('/my_profile')
def redirect_my_profile():
    link = f'/profile/{current_user.id}/head'
    return redirect(link)


#  Получение последних постов из БД
def get_post():
    post = list(db_sess.query(Posts))[:-5:-1]
    return post


#  Получение имени пользователя
def get_author(ids):
    user = db_sess.query(User).filter(User.id == int(ids)).first()
    return user.name


#  Получение изображение профиля пользователя
def get_avatar(ids):
    user = db_sess.query(User).filter(User.id == int(ids)).first()
    return user.avatar


#  Переадресация на песню
@app.route("/redirect-song/<songid>")
def redirect_song(songid):
    return redirect(f'/song/{songid}/head')


#  Страница с ошибкой 404
@app.errorhandler(404)
def not_found(error):
    return render_template('error404.html')


#  Получение названия жанра из БД
def get_genre_name(id_genre):
    genre = db_sess.query(Genre).filter(Genre.id == int(id_genre)).first()
    return genre.name


#  Получение песни по определенному жанру
def get_song_from_genre():
    current_user = get_user_from_session()[0]
    try:
        liked = list(map(int, current_user.genres.split(';')))
        songs = [(db_sess.query(Genre).filter(Genre.id == elem).first(),
                  list(db_sess.query(Song).filter(Song.genre == elem))) for elem in liked]
    except Exception:
        songs = []
    return songs


#  Получение карты по заданому адресу
def search_map(address):
    current_user, userid, username = get_user_from_session()
    response = requests.get(f'http://geocode-maps.yandex.ru/1.x/?apikey={API}&geocode={address}&format=json')
    response = response.json()
    if response:
        try:
            res = ','.join(
                response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos'].split(' '))
            map_resp = requests.get(
                f'https://static-maps.yandex.ru/1.x/?ll={res}&pt={res},pm2vvl&spn=0.002,0.002&l=map')
            p = len(list(db_sess.query(Events).filter(Events.user == int(current_user.id)).all())) + 1
            map_file = f'static/inf/events/concert_{current_user.id}_{p}.png'
            if not map_resp:
                return 'Мы не нашли ничего подходящего'
            try:
                os.remove(map_file)
            except Exception:
                pass
            with open(map_file, "wb") as file:
                file.write(map_resp.content)
            print(map_file)
            return '/' + map_file
        except Exception as error:
            print(error)
            return 'Error'


#  Страница добавление мероприятия
@app.route('/set_event', methods=['GET', 'POST'])
def set_event():
    global map_file
    current_user, userid, username = get_user_from_session()
    if current_user:
        set_address = SetEvent()
        if request.method == 'POST':
            if set_address.update.data:
                map_file = search_map(set_address.address.data)
            elif set_address.public.data:
                event = Events()
                event.date = datetime.datetime(set_address.data.data.year, set_address.data.data.month,
                                               set_address.data.data.day, set_address.time.data.hour,
                                               set_address.time.data.minute)
                event.user = current_user.id
                if map_file != '/static/inf/buttons/base_map.png':
                    event.ll = map_file
                    map_file = '/static/inf/buttons/base_map.png'
                event.description = set_address.address.data
                event.name = set_address.title.data
                db_sess.add(event)
                db_sess.commit()
                return redirect('/')
        return render_template('set_event.html', form=set_address, map_file=map_file, title='Добавить мероприятие')
    else:
        return redirect("/")


#  Переадресация на страницу мероприятия
@app.route('/redirect-event/<id_event>')
def redirect_event(id_event):
    return redirect(f'/event/{id_event}')


#  Страница мероприятия
@app.route('/event/<id_event>')
def event_more(id_event):
    current_user, userid, username = get_user_from_session()
    if current_user:
        event = db_sess.query(Events).filter(Events.id == int(id_event)).first()
        return render_template('event_more.html', event=event, current_user=current_user, title=event.name)
    else:
        return redirect('/')


if __name__ == '__main__':
    main()
