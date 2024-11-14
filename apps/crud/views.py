from apps.crud.forms import UserForm,BodyForm
from apps.crud.models import User
from apps.app import db
from flask import Blueprint,render_template,redirect,url_for,session

from flask_login import login_required


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

@crud.route("/accounts/new", methods=["GET", "POST"])
@login_required

def create_user():
    # UserFormをインスタンス化する
    acontsform = UserForm()
    if acontsform.validate_on_submit():
        # ユーザー情報を取得
        userid = acontsform.userid.data
        username = acontsform.username.data
        password = acontsform.password.data
        
        # フォームの情報をセッションに保存して次の画面へ
        session['loginid'] = userid
        session['username'] = username
        session['password'] = password
        
        # 身体情報入力画面へリダイレクト
        return redirect(url_for("crud.user_body"))

    # 初期表示またはエラー時のcreate.htmlを表示
    return render_template("crud/create.html", form=acontsform)


@crud.route("/accounts/body", methods=["GET", "POST"])
@login_required

def user_body():
    # 身体情報のフォーム
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
    
    # 初期表示またはエラー時の身体情報入力画面.htmlを表示
    return render_template("crud/身体情報入力画面.html", form=bodyform)


@crud.route("/users")
@login_required

def users():
    users = User.query.all()
    return render_template("crud/index.html", users=users)

@crud.route("/users/<user_id>", methods=["GET", "POST"])
@login_required

def edit_user(user_id):
    form = BodyForm()
    # Userモデルを利用してユーザーを取得する
    user = User.query.filter_by(user_id=id).first()
    # formからサブミットされた場合はユーザーを更新しユーザーの一覧画面へリダイレクトする
    if form.validate_on_submit():
        id=user_id,
        username=username,
        password=password,
        sex=sex,
        user.age = form.age.data
        user.height = form.height.data
        user.weight = form.weight.data
        db.session.commit()
        return redirect(url_for("crud.users"))
    # GETの場合はHTMLを返す
    return render_template("crud/edit.html", user=user, form=form)

