# 田端将人
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField,IntegerField,RadioField,FloatField,SelectField
from wtforms.validators import DataRequired, Email, length,NumberRange,Regexp
class SignupUser(FlaskForm):
    userid = StringField(
        "ログインID",
        validators=[
            DataRequired(message="すべての項目を入力してください"),
            Regexp(r'^[a-zA-Z0-9]*$', message="空白無しのまたは半角英数で入力してください")
        ]
    )
    
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="すべての項目を入力してください")
        ]
    )

    password = PasswordField("パスワード", validators=[DataRequired(message="すべての項目を入力してください"),
               Regexp(r'^[a-zA-Z0-9]*$', message="空白無しのまたは半角英数で入力してください")
        ]
    )
    
    submit = SubmitField("次へ")

class CreateBody(FlaskForm):
    age=IntegerField(
        "年齢",
        validators=[
            DataRequired(message="この項目は必須です"),
            NumberRange(0,150,message="正しい数字を入力してください。")
        ]
    )
    sex=RadioField(
        "性別",choices=[('男', '男性'), ('女', '女性')],
        validators=[
            DataRequired('性別を選択してください。')]
    )
    height=FloatField(
        "身長",
        validators=[
                DataRequired(message="この項目は必須です"),
                NumberRange(50,300,message="正しい数字を入力してください。")
            ]
        )

    weight=FloatField(
        "体重",
        validators=[
                DataRequired(message="この項目は必須です"),
                NumberRange(1,150,message="正しい数字を入力してください。")
            ]
        )
    
    submit = SubmitField("登録")

class LoginForm(FlaskForm):
    userid = StringField(
        "ユーザーID",
        validators=[
            DataRequired("ユーザーIDは必須です。"),
        ],
    )
    password = PasswordField("パスワード", validators=[DataRequired("パスワードは必須です。")])
    submit = SubmitField("ログイン")
