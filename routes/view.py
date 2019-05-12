from main import web_app as app
from main import config
from flask import render_template


@app.context_processor
def consts():
    return {
        "USING_SSL": config.USING_SSL,
        "DEBUG": config.DEBUG,
        "APP_NAME": config.APP_NAME,
        "SALT": config.PASSWORD_SALT
    }

# 500错误处理

# @app.errorhandler(Exception)
# def internal_server_error(ex):
#     import traceback
#     traceback.print_exc()
#     return f"{ex.__class__.__name__}: {ex}", 500


@app.route("/")
def view_index():
    return render_template("main.html")


@app.route("/login")
def view_login():
    return render_template("login.html")


@app.route("/register")
def view_register():
    return render_template("register.html")


@app.route("/problem_edit/<int:id>")
def view_edit_problem(id):
    # print(id)
    return render_template("problem_edit.html")


@app.route("/show_problem/<int:id>")
def view_show_problem(id):
    # print(id)
    return render_template("show_problem.html")


@app.route("/show_submission/<int:id>")
def view_show_submission(id):
    # print(id)
    return render_template("show_submission.html")
