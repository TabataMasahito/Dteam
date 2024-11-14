from apps.app import db
from apps.auth.forms import LoginForm,SignupUser,CreateBody
from apps.crud.models import User
from flask import Blueprint, render_template, flash, url_for, redirect, request,session

from flask_login import login_user,logout_user
# Blueprintを使ってauthを生成する
auth = Blueprint(
    "auth",
    __name__,
    template_folder="templates",
    static_folder="static"
)
@auth.route("/")
def index():
    return render_template("auth/index.html")

@auth.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupUser()
    if form.validate_on_submit():
        # ユーザー情報を取得
        userid = form.userid.data
        username = form.username.data
        password = form.password.data

        if User.is_duplicate_userid(userid):
            flash("指定のユーザーIDは登録済みです")
            return redirect(url_for("auth.signup"))

        # フォームの情報をセッションに保存して次の画面へ
        session['userid'] = userid
        session['username'] = username
        session['password'] = password

        # 身体情報入力画面へリダイレクト
        return redirect(url_for("auth.bodycreate"))

    # 初期表示またはエラー時のcreate.htmlを表示
    return render_template("auth/signup.html", form=form)


@auth.route("/bodycreate", methods=["GET", "POST"])

def bodycreate():
    # 身体情報のフォーム
    form = CreateBody()
    if form.validate_on_submit():
        # セッションからユーザー情報を取得
        userid = session.get('userid')
        username = session.get('username')
        password = session.get('password')
        
        # ユーザーを作成する
        user = User(
            id=userid,
            username=username,
            password=password,
            age=form.age.data,
            sex=form.sex.data,
            height=form.height.data,
            weight=form.weight.data
        )
        

        # ユーザーを追加してコミットする
        db.session.add(user)
        db.session.commit()
        login_user(user)
        # セッションから情報を削除
        session.pop('userid', None)
        session.pop('username', None)
        session.pop('password', None)
        next_ = request.args.get("next")
        if next_ is None or not next_.startswith("/"):
            next_ = url_for("exercise.index")
        return redirect(next_)
    # 初期表示またはエラー時の身体情報入力画面.htmlを表示
    return render_template("auth/createbody.html", form=form)





@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # ユーザーIDからユーザーを取得する
        user = User.query.filter_by(id=form.userid.data).first()

        
        # ユーザーが存在しパスワードが一致する場合はログインを許可する
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for("exercise.index"))
        

        # ログイン失敗メッセージを設定する
        flash("ユーザーIDかパスワードが不正です")
    return render_template("auth/login.html", form=form)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))