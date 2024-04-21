from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, TextAreaField, DateField, TimeField
from wtforms.validators import DataRequired
import flask_wtf
import datetime

class LoginForm(flask_wtf.FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegisterForm(flask_wtf.FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Пароль снова', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    about = StringField('Расскажи нам немного о себе!', validators=[DataRequired()])
    submit = SubmitField('Регистрация')


class CommentForm(flask_wtf.FlaskForm):
    comment = TextAreaField('Комментарий')
    public_comment = SubmitField('Оставить')
    like = SubmitField('Понравилось')


class AddSong(flask_wtf.FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    update = SubmitField('Обновить')
    public = SubmitField('Опубликовать')
    link_spotify = StringField('Spotify')
    link_yandex = StringField('Яндекс.Музыка')
    link_youtube = StringField('YouTube')

class SetEvent(flask_wtf.FlaskForm):
    address = StringField('Адрес', validators=[DataRequired()])
    title = StringField('Название', validators=[DataRequired()])
    update = SubmitField('Обновить')
    public = SubmitField('Опубликовать')
    data = DateField(default=datetime.date.today())
    time = TimeField(default=datetime.datetime.now().time())

