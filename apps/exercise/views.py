from flask import Blueprint, render_template
# template_folderを指定する（staticは指定しない）
dt = Blueprint("exercise", __name__, template_folder="templates")
# dtアプリケーションを使ってエンドポイントを作成する
@dt.route("/")
def index():
    return render_template("exercise/index.html")