from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, TextAreaField
from wtforms.validators import DataRequired
import flask_wtf


class LoginForm(flask_wtf.FlaskForm):
    email = StringField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(flask_wtf.FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Пароль снова', validators=[DataRequired()])
    email = EmailField('Почта', validators=[DataRequired()])
    submit = SubmitField('Регистрация')


class CommentForm(flask_wtf.FlaskForm):
    comment = TextAreaField('Комеентарий')
    public_comment = SubmitField('Оставить')
    like = SubmitField('Понравилось')



