#田端将人
from apps.exercise.forms import ModeSelectForm,WeightRecordForm,GoolSettingForm
from flask import Blueprint, render_template, flash, url_for, redirect, request,session,jsonify
from apps.exercise.models import WeightRecord,ExercisePlan
from apps.app import db
from flask_login import login_user,logout_user,login_required,current_user
from datetime import datetime,timedelta,date
from sqlalchemy import desc

# template_folderを指定する（staticは指定しない）
dt = Blueprint("exercise", __name__, template_folder="templates")
# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/")
@login_required
def index():
    return render_template("exercise/index.html")

# dtアプリケーションを使ってmodeselectのエンドポイントを作成する
@dt.route("/modeselect", methods=["GET", "POST"])
@login_required
def mode_select():
    form = ModeSelectForm()
    if form.validate_on_submit():
        mode = form.mode.data
        session['mode'] = mode
        return redirect(url_for("exercise.goal_setting"))

    return render_template("exercise/modeselect.html", form=form)

# dtアプリケーションを使ってgoalsettingのエンドポイントを作成する
@dt.route("/goalsetting", methods=["GET", "POST"])
@login_required
def goal_setting():
    form = GoolSettingForm()
    if form.validate_on_submit():
        mode = session.get('mode')
        getid=current_user.id
        # DB内で同じuser_idを持つレコードの数を取得
        count = ExercisePlan.query.filter_by(user_id=getid).count()
        # 新しいidを生成 (renameにcountを結合)
        new_id = getid+"plan"+str(count + 1)
        exerciseplan = ExercisePlan(
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

# dtアプリケーションを使ってplansettingconpleteのエンドポイントを作成する
@dt.route("/plansettingconplete")
@login_required
def paln_setting_complete():
    return render_template("exercise/plan_setting_complete.html")

# dtアプリケーションを使ってweightrecordのエンドポイントを作成する
@dt.route("/weightrecord", methods=["GET", "POST"])
@login_required
def weight_record():
    form = WeightRecordForm()
    if form.validate_on_submit():
        getid = current_user.id
        # 現在の日付を取得
        today = datetime.now().date()

        # 同じ日付のレコードを取得
        weightrecord = WeightRecord.query.filter_by(user_id=getid, record_at=today).first()

        if weightrecord:
            # レコードが存在する場合は更新
            weightrecord.recordweight = form.recordweight.data
        else:
            # 既存のレコードがない場合は新規作成
            count = WeightRecord.query.filter_by(user_id=getid).count()
            new_id = getid + "weight" + str(count + 1)
            weightrecord = WeightRecord(
                id=new_id,
                user_id=getid,
                recordweight=form.recordweight.data,
                record_at=today  # 現在の日付を設定
            )
            db.session.add(weightrecord)

        db.session.commit()
        return redirect(url_for("exercise.weight_record_complete"))

    return render_template("exercise/weight_record.html", form=form)

# dtアプリケーションを使ってweightrecordconpleteのエンドポイントを作成する
@dt.route("/weightrecordconplete")
@login_required
def weight_record_complete():
    return render_template("exercise/weight_record_complete.html")

# dtアプリケーションを使ってconfirmyourgoalのエンドポイントを作成する
@dt.route("/confirmyourgoal")
@login_required
def confirm_your_goal():
    user_id = current_user.id
    today = date.today()

    record_at = (
        ExercisePlan.query.filter_by(user_id=user_id)
        .order_by(desc(ExercisePlan.record_at))
        .first()
    )
    if record_at:
        record_at = record_at.record_at  # 必要に応じて型変換
        if isinstance(record_at, str):
            record_at = datetime.strptime(record_at, "%Y-%m-%d").date()

    period = (
        ExercisePlan.query.filter_by(user_id=user_id)
        .order_by(desc(ExercisePlan.period))
        .first()
    )
    period = int(period.period)  # 必要に応じて型変換

    
    future_date = record_at + timedelta(days=period)
    remainingdays = future_date - today

    latest_weight_record = (
        WeightRecord.query.filter_by(user_id=user_id)
        .order_by(desc(WeightRecord.record_at))
        .first()
    )
    nowweight = latest_weight_record.recordweight  # 最新の体重

    exercise_plan = ExercisePlan.query.filter_by(user_id=user_id).first()
    goalweight = exercise_plan.goalweight  # 目標体重

    remaining_weight = nowweight - goalweight
    remaining_weight = round(remaining_weight, 1)

    future_date = record_at + timedelta(days=period)
    remainingdays = future_date - today

    return render_template(
        "exercise/confirm_your_goal.html",

        remaining_weight=remaining_weight,
        remainingdays=remainingdays.days
    )

# dtアプリケーションを使ってのエンドポイントを作成する
@dt.route("/useredit")
@login_required
def user_edit():
    return render_template("exercise/user_edit.html")

@dt.route("/api/weight_data")
def weight_data():
    records = WeightRecord.query.order_by(WeightRecord.record_at).all()
    data = [{"date": record.record_at.strftime("%Y-%m-%d"), "weight": record.recordweight} for record in records]
    return jsonify(data)

# dtアプリケーションを使ってweighttransitioncheckのエンドポイントを作成する
@dt.route("/weighttransitioncheck")
def weight_transition_check():
    return render_template("exercise/weight_transition_check.html")
