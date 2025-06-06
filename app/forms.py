from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, SelectField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length, Optional
from flask_wtf.file import FileAllowed, FileRequired
import sqlalchemy as sa
from app import db
from app.models import User, LostFoundItem 


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()]) # Changed label
    password2 = PasswordField(
        'Repeat New Password', validators=[DataRequired(), EqualTo('password')]) # Changed label
    submit = SubmitField('Reset Password') 


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Update Profile') 

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class LostFoundItemForm(FlaskForm):
    item_type = SelectField('Type', choices=[('found', 'Found Item'), ('lost', 'Lost Item')], validators=[DataRequired()])
    title = StringField('Item Title (e.g., "Blue Backpack", "Keys with Red Lanyard")', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Detailed Description', validators=[DataRequired(), Length(min=1, max=500)])
    location = StringField('Location (where found/lost, e.g., "Library 2nd floor", "Cafeteria")', validators=[Optional(), Length(max=140)])
    contact_info = StringField('Your Preferred Contact Info (e.g., Email, Phone Number, Instagram Handle)', validators=[Optional(), Length(max=140)])
    image = FileField('Upload Image (Optional)', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Submit Item')

class SearchForm(FlaskForm):
    search_query = StringField('Search Lost & Found Items', validators=[DataRequired()])
    submit = SubmitField('Search')