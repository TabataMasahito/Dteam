
from werkzeug.security import generate_password_hash
from apps.app import db, login_manager
from flask_login import UserMixin
from datetime import date
from werkzeug.security import check_password_hash, generate_password_hash
class WeightRecord(db.Model):    # テーブル名を指定する
    __tablename__ = "weightrecord"
    # カラムを定義する
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("acount.id"))
    recordweight = db.Column(db.Float)
    record_at = db.Column(db.Date, default=date.now)

class ExercisePlan(db.Model):
    __tablename__ = "exerciseplan"
    # カラムを定義する
    id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("acount.id"))
    mode = db.Column(db.String(5))
    period = db.Column(db.String)
    goalweight = db.Column(db.Float)
    numberexercisesweek = db.Column(db.Integer)
