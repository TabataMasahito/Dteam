from flask import Blueprint, render_template
from apps.exercise.forms import ModeSelectForm,WeightRecordForm,GoolSettingForm
from flask import Blueprint, render_template, flash, url_for, redirect, request,session
from apps.exercise.models import WeightRecord,ExercisePlan
from apps.app import db
from flask_login import login_user,logout_user,login_required,current_user

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
        mode = form.mode.data
        session['mode'] = mode
        return redirect(url_for("exercise.goal_setting"))

    return render_template("exercise/modeselect.html", form=form)

@dt.route("/goalsetting", methods=["GET", "POST"])
@login_required
def goal_setting():
    form = GoolSettingForm()
    if form.validate_on_submit():
        mode = session.get('mode')
        getid=current_user.id
        # DB内で同じuser_idを持つレコードの数を取得
        count = WeightRecord.query.filter_by(user_id=getid).count()
        # 新しいidを生成 (renameにcountを結合)
        new_id = getid+"plan"+count + 1
        exerciseplan = WeightRecord(
            id=new_id,
            user_id=getid,
            mode=mode,
            period=form.period.data,
            goalweight=form.goalweight.data,
            numberexercisesweek=form.numberexercisesweek.data
        )
        db.session.add(exerciseplan)
        db.session.commit()
        return redirect(url_for("exercise.paln_setting_complete"))

        

    return render_template("exercise/goal_setting.html", form=form)

@dt.route("/plansettingconplete")
@login_required
def paln_setting_complete():
    return render_template("exercise.paln_setting_complete.html")




@dt.route("/weightrecord")
@login_required
def weight_record():
    form = WeightRecordForm()
    return render_template("exercise/weight_record.html", form=form)



@dt.route("/confirmyourgoal")
@login_required
def confirm_your_goal():
    return render_template("exercise/confirm_your_goal.html")


