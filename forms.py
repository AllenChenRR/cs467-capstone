from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import widgets, StringField, PasswordField, SubmitField, SelectField, TextAreaField, SelectMultipleField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
import constants as const
# This class was built with the assistance of the following tutorial:
# "Python Flask Tutorial: Full-Featured Web App Part 3 - Forms and User Input"
# Link: https://youtu.be/UIJKdCIEXUQ

DISPOSITIONS = const.DISPOSITIONS_FOR_FORMS
CAT_BREEDS = const.CAT_BREEDS
DOG_BREEDS = const.DOG_BREEDS
OTHER_BREEDS = const.OTHER_BREEDS
ANIM_TYPES = const.ANIM_TYPES
AVAILABILITIES = const.AVAILABILITIES

ANIM_SEARCH_TYPES = const.ANIM_SEARCH_TYPES
NO_BREEDS =  const.NO_BREEDS
SEARCH_AVAILABILITIES = const.SEARCH_AVAILABILITIES


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

class SearchPetForm(FlaskForm):
    date = StringField('Create Date')
    name = StringField("Name")
    animal_type = SelectField('Animal Type', choices=ANIM_SEARCH_TYPES)
    breed = SelectField('Breed')
    disposition = MultiCheckboxField('Disposition', choices=DISPOSITIONS)
    availability = SelectField('Availability', choices=SEARCH_AVAILABILITIES)
    submit = SubmitField("Search")
    
    # def validate_date(form, field):
    #     if format('%m-%d-%Y'):
    #         raise ValidationError('Must be in format month/day/year')