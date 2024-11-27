#田端将人
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField,IntegerField,RadioField,FloatField,SelectField,TextAreaField
from wtforms.validators import DataRequired, Email, length,NumberRange

class ModeSelectForm(FlaskForm):
    mode = RadioField('運動モード', choices=[
        ('筋トレ', '筋トレモード'),
        ('ダイエット', 'ダイエットモード'),
        ('健康維持', '健康維持モード')
    ], validators=[DataRequired('モードを選択してください。')
    ])
    submit = SubmitField('次へ')

class GoolSettingForm(FlaskForm):
    period = IntegerField(
        "期間",
        validators=[
            DataRequired(message="すべての項目を入力してください")
        ]
    )
    goalweight = FloatField(
        "目標体重",
        validators=[
            DataRequired(message="体重は必須です。"),
            NumberRange(1,150,message="正しい数字を入力してください。")
        ]
    )
    numberexercisesweek = IntegerField(
        "週の運動回数",
        validators=[
            DataRequired(message="体重は必須です。"),
            NumberRange(1,7,message="正しい数字を入力してください。")
        ]
        
    )
    submit = SubmitField('登録')
class WeightRecordForm(FlaskForm):
    recordweight = FloatField(
        "体重",
        validators=[
                DataRequired(message="体重は必須です。"),
                NumberRange(1,150,message="正しい数字を入力してください。")
            ]
        )
    submit = SubmitField('登録')
    
class ExerciseForm(FlaskForm):
    exerciseitem = RadioField('運動器具', choices=[
        ("有", "有"),
        ("無", "無")

    ], validators=[DataRequired('この項目は必須です')
    ])
    strength = RadioField('運動強度', choices=[
        ("弱", "弱"),
        ("中", "中"),
        ("強", "強")
    ], validators=[DataRequired('この項目は必須です')
    ])
    minutes=IntegerField(
        "運動時間",
        validators=[
            DataRequired(message="この項目は必須です")
        ])
    submit = SubmitField('作成')
