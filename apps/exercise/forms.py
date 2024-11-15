from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField,IntegerField,RadioField,FloatField,SelectField
from wtforms.validators import DataRequired, Email, length,NumberRange

class ModeSelectForm(FlaskForm):
    mode = RadioField('運動モード', choices=[
        ('筋トレ', '筋トレモード'),
        ('ダイエット', 'ダイエットモード'),
        ('健康維持', '健康維持モード')
    ], validators=[DataRequired()])
    submit = SubmitField('次へ')