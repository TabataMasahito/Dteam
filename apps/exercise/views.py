#田端将人
from apps.exercise.forms import ModeSelectForm,WeightRecordForm,GoalSettingForm,ExerciseForm
from flask import Blueprint, render_template, flash, url_for, redirect,session,jsonify
from apps.exercise.models import WeightRecord,ExercisePlan,ExerciseHistory
from apps.app import db
from flask_login import login_required,current_user
from datetime import datetime,timedelta,date
from sqlalchemy import desc,func
import google.generativeai as genai
from flask import request
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
        # 型の修正
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
            return render_template("exercise/plan_setting_error.html",user_record_exists=user_record_exists,future_date=future_date)
        

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
    form = GoalSettingForm()
    mode = session.get('mode')  # Retrieve the mode from session
    
    if form.validate_on_submit():
        getid = current_user.id
        # DB内で同じuser_idを持つレコードの数を取得
        count = ExercisePlan.query.filter_by(user_id=getid).count()
        # 新しいidを生成 (renameにcountを結合)
        new_id = getid + "plan" + str(count + 1)
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
    
    return render_template("exercise/goal_setting.html", form=form, mode=mode)

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
    user_id=current_user.id
    today = date.today()
    exercise_records = ExercisePlan.query.filter_by(user_id=user_id).all()

    # 運動プランが設計されていない場合はエラー画面へ
    if not exercise_records:
        return render_template("exercise/exercise_error.html")
    

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

    exercise_plan = ExercisePlan.query.filter_by(user_id=user_id).order_by(desc(ExercisePlan.period)).first()
    goalweight = exercise_plan.goalweight  # 目標体重

    remaining_weight = nowweight - goalweight if nowweight - goalweight > 0 else goalweight-nowweight
    remaining_weight = round(remaining_weight, 1)

    future_date = record_at + timedelta(days=period)
    remainingdays = future_date - today

    # 前回のプランが終了していない場合はエラー画面へ
    if remainingdays.days<=0:
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

    
    # レコードがある場合は通常ページを表示
    return render_template("exercise/weight_transition_check.html", records=user_records)



# 運動メニュー提案機能_設定
@dt.route("/exercise_menu_setting", methods=["GET", "POST"])
@login_required  # ログインしていないとアクセスできないようにする
def exercise_menu_setting():
    user_id=current_user.id
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
        if remainingdays.days <= 0 :
            return render_template("exercise/exercise_error.html")
    else:
            return render_template("exercise/exercise_error.html")




    munu_history_records = ExerciseHistory.query.filter_by(user_id=user_id,record_at=today).count()
    if munu_history_records>=3:
        return render_template("exercise/exercise_menu_error.html")


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
    GOOGLE_API_KEY = "AIzaSyCIAKpoUtUYjyuHtqnhs9-OEU1kGjwetYI"
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
            "現在の体重：{}kg、運動を行う期間：{}日です。また今日の運動メニューは運動器具や道具は：{}、\n"
            "運動の強度（強、中、弱）の中で：{}、運動時間は{}分と設定されています。\n"
            "では本日の運動メニューを教えてください。メニュー以外の情報は必要ありません。またウォームアップ、エクササイズ、クールダウンの３つに分け、すべて含めて運動時間内に終わるようにしてください。"
        ).format(mode, sex, age, height, weight, goal_weight, nowweight, period, exerciseitem, strength, minutes)

        # チャットの開始と応答取得
    chat = model.start_chat(history=[])
    response = chat.send_message(question)

    def format_response(response_text):
        # 応答が箇条書き形式になるよう整形
        lines = response_text.split('\n')
        formatted = []
        for line in lines:
            if line.strip():
                formatted.append(f"{line.strip()}")
        return '\n'.join(formatted)

    formatted_response = format_response(response.text)


    count = ExerciseHistory.query.filter_by(user_id=user_id).count()
            # 新しいidを生成 (renameにcountを結合)
    new_id = user_id+"menuhistory"+str(count + 1)

    exercise_menuhistory = ExerciseHistory(
        id=new_id,
        user_id=user_id,
        menuhistory=formatted_response,
        exercise_item=exerciseitem,
        strength=strength,
        minutes=minutes
            )
    db.session.add(exercise_menuhistory)
    db.session.commit()

    session['menu'] = formatted_response



    return redirect(url_for("exercise.exercise_menuscreen"))


# 運動メニューをhtml上に表示する
@dt.route('/exercise_menuscreen')
@login_required  # ログインしていないとアクセスできないようにする
def exercise_menuscreen():
    username = current_user.username
    formatted_response = session.get('menu')
    return render_template('exercise/exercise_menu.html',username=username,response=formatted_response)


# 履歴を表示する機能
@dt.route('/menu_history', methods=['GET', 'POST'])
@login_required
def menu_history():
    user_id = current_user.id
    # デフォルトでは今日の日付
    date_str = request.args.get('date', str(date.today()))
    try:
        # クエリパラメータで渡された日付文字列を日付型に変換
        history_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        # 不正な日付が渡された場合は今日の日付を使用
        history_date = date.today()

    menuhistory = ExerciseHistory.query.filter_by(user_id=user_id, record_at=history_date).all()
    return render_template('exercise/exercise_menu_history.html', 
                           menuhistory=menuhistory, 
                           username=current_user.username,
                           selected_date=history_date)









# Xにポストする機能

@dt.route("/post")
@login_required
def post():
    today = date.today()
    exercise_records = ExerciseHistory.query.filter_by(user_id=current_user.id,record_at=today).all()
    if not exercise_records:
        return render_template("exercise/post_error.html")
    
    exercise_time = db.session.query(func.sum(ExerciseHistory.minutes)).filter_by(user_id=current_user.id, record_at=today).scalar()    
    user_record_exists = ExercisePlan.query.filter_by(user_id=current_user.id).order_by(desc(ExercisePlan.record_at)).first()
 
    return render_template("exercise/post.html",exercise_time=exercise_time,mode=user_record_exists.mode)
 