from flask import Blueprint, render_template
from apps.exercise.forms import ModeSelectForm,WeightRecordForm,GoolSettingForm
from flask import Blueprint, render_template, flash, url_for, redirect, request,session

from flask_login import login_user,logout_user,login_required

# template_folderを指定する（staticは指定しない）
dt = Blueprint("exercise", __name__, template_folder="templates")
# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/")
@login_required
def index():
    return render_template("exercise/index.html")

@dt.route("/modeselect", methods=["GET", "POST"])
@login_required
def mode_select():
    form = ModeSelectForm()
    if form.validate_on_submit():
        # ユーザー情報を取得

        # 身体情報入力画面へリダイレクト
        return redirect(url_for("exercise.goal_setting"))

    return render_template("exercise/modeselect.html", form=form)

@dt.route("/weightrecord")
@login_required
def weight_record():
    form = WeightRecordForm()
    return render_template("exercise/weight_record.html", form=form)

@dt.route("/goalsetting")
@login_required
def goal_setting():
    form = GoolSettingForm()
    return render_template("exercise/goal_setting.html", form=form)

@dt.route("/confirmyourgoal")
@login_required
def confirm_your_goal():
    return render_template("exercise/confirm_your_goal.html")
