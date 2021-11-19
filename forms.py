from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import widgets, StringField, PasswordField, SubmitField, SelectField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
# This class was built with the assistance of the following tutorial:
# "Python Flask Tutorial: Full-Featured Web App Part 3 - Forms and User Input"
# Link: https://youtu.be/UIJKdCIEXUQ

DISPOSITIONS = [("good with children", "Good with children"), ("good with other animals",
                "Good with other animals"), ("animal must be leashed at all times",
                "Animal must be leashed at all times")]
CAT_BREEDS = [("maine coon", "Maine Coon"), ("siamese", "Siamese"), ("other", "Other")]
DOG_BREEDS = [("retriever", "Retriever"), ("bulldog", "Bulldog"), ("other", "Other")]
OTHER_BREEDS = [('other', 'Other')]
ANIM_TYPES = [('cat', 'Cat'), ('dog', 'Dog'), ('other', 'Other')]
AVAILABILITIES = [('available', 'Available'), ('pending', 'Pending'), ('adopted', 'Adopted')]


# Widgets
class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


# Forms
# ---------------------------------------------------------------------------
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
    animal_type = SelectField('Animal Type', choices=ANIM_TYPES)
    breed = SelectField('Breed', choices=CAT_BREEDS)
    disposition = MultiCheckboxField('Disposition', choices=DISPOSITIONS)
    availability = SelectField('Availability', choices=AVAILABILITIES)
    description = TextAreaField('Description')
    image = FileField('Image', validators=[FileRequired(), FileAllowed(['png', 'jpeg', 'jpg'], "Invalid image format!")
    ])
    submit = SubmitField('Submit')


class EditPetForm(FlaskForm):
    name = StringField("Name",  validators=[Optional(False), DataRequired(), Length(min=2, max=20)])
    animal_type = SelectField('Animal Type', choices=ANIM_TYPES)
    breed = SelectField('Breed')
    disposition = MultiCheckboxField('Disposition', choices=DISPOSITIONS)
    availability = SelectField('Availability', choices=AVAILABILITIES)
    description = TextAreaField('Description')
    image = FileField('Image', validators=[FileAllowed(['png', 'jpeg', 'jpg'], "Invalid image format!")])
    submit = SubmitField("Update")
