from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
# This class was built with the assistance of the following tutorial: 
# "Python Flask Tutorial: Full-Featured Web App Part 3 - Forms and User Input"
# Link: https://youtu.be/UIJKdCIEXUQ

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=18)])
    confirm_password = PasswordField('Confirm Password', 
                                        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=4)])
    submit = SubmitField('Login')

class AccountForm(FlaskForm):
    first_name = StringField('First Name', validators=[Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[Length(min=2, max=20)])
    email = StringField('Email', validators=[Email()])
    password = PasswordField('Enter Current Password To Update Account', validators=[DataRequired()])
    new_password = PasswordField('New Password')
    confirm_password = PasswordField('Confirm Password', validators=[EqualTo('new_password', "Passwords must match")])
    submit = SubmitField('Update')

    def validate_new_password(form, field):
        if field.data and not (len(field.data) >= 4):
            raise ValidationError("Password must be at least 4 characters")

class AddPetForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    animal_type = SelectField('Animal Type', choices=[('cat', 'Cat'), ('dog', 'Dog'), ('other', 'Other')])
    breed = StringField('Breed', validators=[DataRequired(), Length(min=2, max=20)])
    disposition = SelectField('Disposition', choices=[('friendly', 'Friendly'), ('timid', 'Timid'), ('anxious', 'Anxious')])
    availability = SelectField('Availability', choices=[('available', 'Available'), ('pending', 'Pending'), ('adopted', 'Adopted')])
    description = StringField('Description', validators=[DataRequired()])
    image = FileField('Image')
    submit = SubmitField('Submit')
