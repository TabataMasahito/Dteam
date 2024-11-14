
from werkzeug.security import generate_password_hash
from apps.app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
class User(db.Model, UserMixin):    # テーブル名を指定する
    __tablename__ = "acount"
    # カラムを定義する
    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String, index=True)
    password_hash = db.Column(db.String)
    age = db.Column(db.String(3))
    sex = db.Column(db.String(1))
    height = db.Column(db.Float)
    weight = db.Column(db.Float)

    @property
    def password(self):
        raise AttributeError("読み取り不可")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ユーザーIDの重複チェックをする
    @staticmethod
    def is_duplicate_userid(userid):
        return User.query.filter_by(id=userid).first() is not None

# ログインしているユーザー情報を取得する関数を作成する
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
