from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, EmailField, PasswordField, SubmitField
from wtforms.validators import InputRequired, EqualTo, Length, DataRequired


class CreateBookForm(FlaskForm):
    book_name = StringField(
        validators=[
            InputRequired(),
        ],
    )

    author_name = StringField(
        validators=[
            InputRequired(),
        ],
    )

    release_year = IntegerField(
        validators=[
            InputRequired(),
        ],
    )

    book_copy = IntegerField(
        validators=[
            InputRequired(),
        ],
    )


class LoginForm(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(),
        ],
    )

    password = StringField(
        validators=[
            InputRequired(),
        ],
    )


class RegisterForm(FlaskForm):
    username = StringField(
        validators=[
            InputRequired(),
        ],
    )

    password = StringField(
        validators=[
            InputRequired(),
        ],
    )

    repeat_password = StringField(
        validators=[
            EqualTo(
                fieldname='password',
                message="Passwords don't match",
            ),
        ],
    )

    full_name = StringField(
        validators=[
            InputRequired(),
        ]
    )

    email = EmailField(
        validators=[
            InputRequired(),
        ]
    )

    role = EmailField(
        validators=[
            InputRequired(),
        ]
    )


class ChangePasswordForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')