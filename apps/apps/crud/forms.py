from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField,IntegerField,RadioField,FloatField
from wtforms.validators import DataRequired, Email, length,NumberRange
# ユーザー新規作成とユーザー編集フォームクラス
class UserForm(FlaskForm):
    userid = StringField(
        "ログインID",
        validators=[
            DataRequired(message="ログインIDは必須です。"),
        ]
    )
    # ユーザーフォームのusername属性のラベルとバリデータを設定する
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="ユーザー名は必須です。")        ],
    )

    # ユーザーフォームpassword属性のラベルとバリデータを設定する
    password = PasswordField("パスワード", validators=[DataRequired(message="パスワードは必須です。")])
    # ユーザーフォームsubmitの文言を設定する
    submit = SubmitField("次へ")

class BodyForm(FlaskForm):
    age=IntegerField(
        "年齢",
        validators=[
            DataRequired(message="年齢は必須です。"),
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
                DataRequired(message="身長は必須です。"),
                NumberRange(1,300,message="正しい数字を入力してください。")
            ]
        )

    weight=FloatField(
        "体重",
        validators=[
                DataRequired(message="体重は必須です。"),
                NumberRange(1,150,message="正しい数字を入力してください。")
            ]
        )
    
    submit = SubmitField("登録")
