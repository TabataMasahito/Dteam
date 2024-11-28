# 田端将人
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField,IntegerField,RadioField,FloatField,SelectField
from wtforms.validators import DataRequired, Email, length,NumberRange
# ユーザー新規作成とユーザー編集フォームクラス
class SignupUser(FlaskForm):
    userid = StringField(
        "ログインID",
        validators=[
            DataRequired(message="すべての項目を入力してください"),
        ]
    )
    # ユーザーフォームのusername属性のラベルとバリデータを設定する
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="すべての項目を入力してください")        ],
    )

    # ユーザーフォームpassword属性のラベルとバリデータを設定する
    password = PasswordField("パスワード", validators=[DataRequired(message="すべての項目を入力してください")])
    # ユーザーフォームsubmitの文言を設定する
    submit = SubmitField("次へ")

class CreateBody(FlaskForm):
    age=IntegerField(
        "年齢",
        validators=[
            DataRequired(message="すべての項目を入力してください"),
            NumberRange(1,150,message="正しい数字を入力してください。")
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
                DataRequired(message="すべての項目を入力してください"),
                NumberRange(1,300,message="正しい数字を入力してください。")
            ]
        )

    weight=FloatField(
        "体重",
        validators=[
                DataRequired(message="すべての項目を入力してください"),
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
