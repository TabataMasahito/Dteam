#田端将人
from apps.exercise.forms import ModeSelectForm,WeightRecordForm,GoolSettingForm,ExerciseForm
from flask import Blueprint, render_template, flash, url_for, redirect,session,jsonify
from apps.exercise.models import WeightRecord,ExercisePlan
from apps.app import db
from flask_login import login_required,current_user
from datetime import datetime,timedelta,date
from sqlalchemy import desc
import google.generativeai as genai
# template_folderを指定する（staticは指定しない）
dt = Blueprint("exercise", __name__, template_folder="templates")
# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/")
@login_required
def index():
    return render_template("exercise/index.html")

#プラン設計機能_モード選択
# dtアプリケーションを使ってmodeselectのエンドポイントを作成する
@dt.route("/modeselect", methods=["GET", "POST"])
@login_required
def mode_select():
    user_id = current_user.id
    today = date.today()
    user_record_exists = ExercisePlan.query.filter_by(user_id=user_id).order_by(desc(ExercisePlan.record_at)).first()
    if user_record_exists: 

        # 残り日数を計算
        record_at = (
            ExercisePlan.query.filter_by(user_id=user_id)
            .order_by(desc(ExercisePlan.record_at))
            .first()
        )
        if record_at:
            record_at = record_at.record_at  
            if isinstance(record_at, str):
                record_at = datetime.strptime(record_at, "%Y-%m-%d").date()

        Period = (
            ExercisePlan.query.filter_by(user_id=user_id)
            .order_by(desc(ExercisePlan.period))
            .first()
        )
        Period = int(Period.period) 

        
        future_date = record_at + timedelta(days=Period)
        remainingdays = future_date - today

        # まだ過去に設定したプランの日数が残っている場合はエラー画面へ
        if remainingdays.days >= 1:
            return render_template("exercise/plan_setting_error.html")
        

    form = ModeSelectForm()
    if form.validate_on_submit():
        mode = form.mode.data
        session['mode'] = mode
        return redirect(url_for("exercise.goal_setting"))

    return render_template("exercise/modeselect.html", form=form)


#プラン設計機能_目標設定
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


#プラン設計機能_設定完了
@dt.route("/plansettingconplete")
@login_required
def paln_setting_complete():
    return render_template("exercise/plan_setting_complete.html")



# 体重記録機能
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



#体重記録機能_記録完了
@dt.route("/weightrecordconplete")
@login_required
def weight_record_complete():
    return render_template("exercise/weight_record_complete.html")



# 目標確認機能
@dt.route("/confirmyourgoal")
@login_required
def confirm_your_goal():

    user_id = current_user.id
    user_records = WeightRecord.query.filter_by(user_id=user_id).all()
    # 最新の体重が記録されているかチェック
    if not user_records:
        # レコードがない場合はエラーページにリダイレクト
        return render_template("exercise/weight_recode_error.html")
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
    mode=period.mode
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

    remaining_weight = nowweight - goalweight if nowweight - goalweight > 0 else goalweight-nowweight
    remaining_weight = round(remaining_weight, 1)

    future_date = record_at + timedelta(days=period)
    remainingdays = future_date - today
    if remainingdays.days==0:
           return render_template(
        "exercise/goal.html") 

    return render_template(
        "exercise/confirm_your_goal.html",

        remaining_weight=remaining_weight,
        remainingdays=remainingdays.days,
        nowweight=nowweight,
        goalweight=goalweight,
        mode=mode

    )


# 体重グラフ化機能
@dt.route("/api/weight_data")
@login_required  # ログインしていないとアクセスできないようにする
def weight_data():
    # ログイン中のユーザーのIDでフィルタリング
    records = WeightRecord.query.filter_by(user_id=current_user.id).order_by(WeightRecord.record_at).all()
   
    # データを整形
    data = [
        {"date": record.record_at.strftime("%Y-%m-%d"), "weight": record.recordweight}
        for record in records
    ]

    return jsonify(data)
@dt.route("/weighttransitioncheck")
@login_required  # ログインしていないとアクセスできないようにする
def weight_transition_check():
    user_id=current_user.id
    user_records = WeightRecord.query.filter_by(user_id=user_id).all()
    if not user_records:
        # レコードがない場合はエラーページにリダイレクト
        return render_template("exercise/weight_recode_error.html")
    
    # レコードがある場合は通常ページを表示
    return render_template("exercise/weight_transition_check.html", records=user_records)



# 運動メニュー提案機能_設定
@dt.route("/exercise_menu_setting", methods=["GET", "POST"])
@login_required  # ログインしていないとアクセスできないようにする
def exercise_menu_setting():
    user_id=current_user.id
    today = date.today()
    exercise_records = WeightRecord.query.filter_by(user_id=user_id).all()
    if not exercise_records:
        # レコードがない場合はエラーページにリダイレクト
        return render_template("exercise/exercise_error.html")
    user_record_exists = ExercisePlan.query.filter_by(user_id=user_id).order_by(desc(ExercisePlan.record_at)).first()
    if user_record_exists: 

        # 残り日数を計算
        record_at = (
            ExercisePlan.query.filter_by(user_id=user_id)
            .order_by(desc(ExercisePlan.record_at))
            .first()
        )
        if record_at:
            record_at = record_at.record_at  
            if isinstance(record_at, str):
                record_at = datetime.strptime(record_at, "%Y-%m-%d").date()

        Period = (
            ExercisePlan.query.filter_by(user_id=user_id)
            .order_by(desc(ExercisePlan.period))
            .first()
        )
        Period = int(Period.period) 

        
        future_date = record_at + timedelta(days=Period)
        remainingdays = future_date - today

        # まだ過去に設定したプランの日数が残っている場合はエラー画面へ
        if remainingdays.days <= 0 :
            return render_template("exercise/exercise_error.html")



    user_records = WeightRecord.query.filter_by(user_id=user_id).all()
    if not user_records:
        # レコードがない場合はエラーページにリダイレクト
        return render_template("exercise/weight_recode_error.html")
    exerciseform=ExerciseForm()
    if exerciseform.validate_on_submit():
        exerciseitem = exerciseform.exerciseitem.data
        strength = exerciseform.strength.data
        minutes = exerciseform.minutes.data
            
        session['exerciseitem'] = exerciseitem
        session['strength'] = strength
        session['minutes'] = minutes
        return redirect(url_for("exercise.exercise_menu"))

    return render_template("exercise/exercise_menu_setting.html", form=exerciseform)




# 運動メニュー提案機能
@dt.route('/exercise_menu')
@login_required  # ログインしていないとアクセスできないようにする
def exercise_menu():
    GOOGLE_API_KEY = "AIzaSyBqpBn0IK3SHtdlNTlyenP2APlj3Qz9LUs"
    genai.configure(api_key=GOOGLE_API_KEY)

    # モデルの設定
    model = genai.GenerativeModel("gemini-pro")
    user_id = current_user.id

    sex=current_user.sex
    height=current_user.height
    weight=current_user.weight
    age=current_user.age

    latest_weight_record = (WeightRecord.query.filter_by(user_id=user_id).order_by(desc(WeightRecord.record_at)).first())
    nowweight=latest_weight_record.recordweight
    exerciseplan =(ExercisePlan.query.filter_by(user_id=user_id).order_by(desc(ExercisePlan.record_at)).first())
    goal_weight=exerciseplan.goalweight
    mode=exerciseplan.mode
    period=exerciseplan.period
    # numberexercisesweek=exerciseplan.numberexercisesweek
    exerciseitem = session.get('exerciseitem')
    strength = session.get('strength')
    minutes = session.get('minutes')

    question = (
            "あなたはパーソナルトレーナーです。以下のユーザーの目的と期間に適した運動メニューを丁寧な言葉遣いで提案してください。\n"
            "運動の目的：{}、性別：{}、年齢：{}歳、身長：{}cm、初期の体重：{}kg、目標とする体重：{}kg、\n"
            "現在の体重：{}kg、運動を行う期間：{}日です。また今日の運動メニューは運動器具は：{}、\n"
            "運動の強度（強、中、弱）の中で：{}、運動時間は{}分と設定されています。\n"
            "では本日の運動メニューを教えてください。メニュー以外の情報は必要ありません。またウォームアップ、エクササイズ、クールダウンの３つに分け、すべて含めて運動時間内に終わるようにしてください。"
        ).format(mode, sex, age, height, weight, goal_weight, nowweight, period, exerciseitem, strength, minutes)

        # チャットの開始と応答取得
    chat = model.start_chat(history=[])
    response = chat.send_message(question)

    # 応答のフォーマット処理
    def format_response(response_text):
        # 応答が箇条書き形式になるよう整形
        lines = response_text.split('\n')
        formatted = []
        for line in lines:
            if line.strip():
                formatted.append(f"{line.strip()}")
        return '\n'.join(formatted)

    formatted_response = format_response(response.text)

    return render_template(
            'exercise/exercise_menu.html',
            question=question,
            response=formatted_response,
            username=current_user.username
        )