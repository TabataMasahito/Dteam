from apps.crud.forms import UserForm,BodyForm,EditBodyForm,DeleteForm
from apps.crud.models import User
from apps.exercise.models import ExercisePlan,WeightRecord

from apps.app import db
from flask import Blueprint,render_template,redirect,url_for,session,request

from flask_login import login_required, current_user


crud=Blueprint(
    "crud",
    __name__,
    template_folder="templates",
    static_folder="static"
)


@crud.route("/")
@login_required
def index():
    return render_template("crud/index.html")

# user情報のエンドポイント
@crud.route("/accounts/new", methods=["GET", "POST"])
@login_required

def create_user():
    acontsform = UserForm()
    if acontsform.validate_on_submit():
        userid = acontsform.userid.data
        username = acontsform.username.data
        password = acontsform.password.data
        
        session['loginid'] = userid
        session['username'] = username
        session['password'] = password
        
        # 身体情報入力画面へリダイレクト
        return redirect(url_for("crud.user_body"))

    # エラー時のcreate.htmlを表示
    return render_template("crud/create.html", form=acontsform)


# 身体情報のエンドポイント
@crud.route("/accounts/body", methods=["GET", "POST"])
@login_required

def user_body():
    bodyform = BodyForm()
    if bodyform.validate_on_submit():
        # セッションからユーザー情報を取得
        userid = session.get('loginid')
        username = session.get('username')
        password = session.get('password')
        
        # ユーザーを作成する
        user = User(
            id=userid,
            username=username,
            password=password,
            age=bodyform.age.data,
            sex=bodyform.sex.data,
            height=bodyform.height.data,
            weight=bodyform.weight.data
        )
        
        # ユーザーを追加してコミットする
        db.session.add(user)
        db.session.commit()
        
        # セッションから情報を削除
        session.pop('loginid', None)
        session.pop('username', None)
        session.pop('password', None)

        # ユーザーの一覧画面へリダイレクトする
        return redirect(url_for("crud.users"))
    
    # エラー時の身体情報入力画面.htmlを表示
    return render_template("crud/身体情報入力画面.html", form=bodyform)

# dtアプリケーションを使ってのエンドポイントを作成する
@crud.route("/useredit/<user_id>", methods=["GET", "POST"])
@login_required
def user_edit(user_id):
    bodyform = EditBodyForm()

    # Userモデルを利用してユーザーを取得する
    user = current_user  # ログイン中のユーザーを取得

    if request.method == "GET":  # GETリクエストの場合、初期値を設定
        bodyform.age.data = user.age
        bodyform.height.data = user.height
        bodyform.weight.data = user.weight

    # formからサブミットされた場合はメニュー画面へリダイレクトする
    if bodyform.validate_on_submit():
        user.age = bodyform.age.data
        user.height = bodyform.height.data
        user.weight = bodyform.weight.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("crud.update_complete"))
    
    # GETの場合はHTMLを返す
    return render_template("crud/user_edit.html", user=user, form=bodyform)

@crud.route("/updatecomplete")
@login_required
def update_complete():
    return render_template("crud/update_complete.html")

#@crud.route("/confirmdeletion")
#@login_required
#def confirm_deletion():
#    return render_template("crud/confirm_deletion.html")

#@crud.route("/deleteuser", methods=["POST", "GET"])
#@login_required
#def delete_current_user():
#    form = DeleteForm()  # 削除確認用フォーム
#    if form.validate_on_submit():  # POSTリクエストでフォームが送信された場合
#            # 関連データとユーザー自体を削除
#            db.session.query(ExercisePlan).filter_by(user_id=current_user.id).delete()
#            db.session.query(WeightRecord).filter_by(user_id=current_user.id).delete()
#            db.session.query(User).filter_by(id=current_user.id).delete()
#            db.session.commit()
#            return redirect(url_for("auth.signup"))  # 削除後にサインアップ画面へリダイレクト
#    return render_template("crud/confirm_deletion.html", form=form)

@crud.route("/deleteuser/<user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    form = DeleteForm()
    if form.validate_on_submit():
        user = current_user
        # 外部キー制約を無視して関連レコードを削除する（依存レコードも削除する）
        db.session.query(WeightRecord).filter(WeightRecord.user_id==user.id).delete()
        db.session.query(ExercisePlan).filter(ExercisePlan.user_id==user.id).delete()

        # Userテーブルの該当ユーザーを削除
        db.session.query(User).filter(User.id==user.id).delete()

        # 変更をコミット
        db.session.commit()
        return redirect(url_for("auth.signup"))
    return render_template("crud/confirm_deletion.html", form=form, user=user)
