from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Anonymous Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
                raise ValidationError('Please use a different anonymous username.')

class LoginForm(FlaskForm):
    username = StringField('Anonymous Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class PostForm(FlaskForm):
    body = TextAreaField('What\'s on your mind, engineer?', validators=[DataRequired(), Length(min=1, max=1000)])
    channel = SelectField('Channel', choices=[
        ('general', 'General Engineering'),
        ('computer_science', 'Computer Science and Software Engineering'),
        ('computer_eng', 'Computer Engineering'),
        ('electrical_eng', 'Electrical Engineering'),
        ('civil_eng', 'Civil Engineering'),
        ('mechanical_eng', 'Mechanical Engineering'),
        ('chemical_eng', 'Chemical Engineering'),
        ('biomedical_eng', 'Biomedical Engineering'),
        ('mechatronics', 'Mechatronics'),
        ('eng_research', 'Engineering Research')
        # will add more if needed
    ], validators=[DataRequired()])
    submit = SubmitField('Post Anonymously')


class CommentForm(FlaskForm):
    body = TextAreaField('Add a comment....', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Comment')