from main import web_app as app
from main import config
from flask import render_template


@app.context_processor
def consts():
    return {
        "DEBUG": config.DEBUG,
        "APP_NAME": config.APP_NAME,
        "SALT": config.PASSWORD_SALT
    }

@app.route("/")
def view_index():
    return render_template("main.html")


@app.route("/login")
def view_login():
    return render_template("login.html")


@app.route("/register")
def view_register():
    return render_template("register.html")

@app.route("/problems")
@app.route("/problems/<int:id>")
def view_problems(id=-1):
    return render_template("problems.html")
@app.route("/submissions")
@app.route("/submissions/<int:id>")
def view_submissions(id=-1):
    return render_template("submissions.html")
@app.route("/discussions/<string:path>/<int:page>")
def view_discussions(path,page):
    return render_template("discussions.html")


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
@app.route("/show_discussion/<int:id>")
def view_show_discussion(id):
    # print(id)
    return render_template("show_discussion.html")
@app.route("/profile/<int:id>")
def view_profile(id):
    return render_template("profile.html")