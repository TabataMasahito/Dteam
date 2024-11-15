from flask import Blueprint, render_template
from apps.exercise.forms import ModeSelectForm
from flask import Blueprint, render_template, flash, url_for, redirect, request,session

from flask_login import login_user,logout_user

# template_folderを指定する（staticは指定しない）
dt = Blueprint("exercise", __name__, template_folder="templates")
# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/")
def index():
    return render_template("exercise/index.html")

@dt.route("/modeselect", methods=["GET", "POST"])
def mode_select():
    form = ModeSelectForm()
    if form.validate_on_submit():
        # ユーザー情報を取得

        # 身体情報入力画面へリダイレクト
        return redirect(url_for("auth.bodycreate"))

    return render_template("exercise/modeselect.html", form=form)

@dt.route("/weightrecord")
def weight_record():
    return render_template("exercise/weight_record.html")
