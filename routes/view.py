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
    return render_template("user/login.html")


@app.route("/register")
def view_register():
    return render_template("user/register.html")


@app.route("/ranklist/<int:id>")
def view_global_ranklist(id):
    return render_template("ranklist.html")


@app.route("/problems")
@app.route("/problems/<int:id>")
def view_problems(id=-1):
    return render_template("problem/problems.html")


@app.route("/submissions")
@app.route("/submissions/<int:id>")
def view_submissions(id=-1):
    return render_template("submissions.html")


@app.route("/discussions/<string:path>/<int:page>")
def view_discussions(path, page):
    return render_template("discussions.html")


@app.route("/problem_edit/<int:id>")
def view_edit_problem(id):
    # print(id)
    return render_template("problem/problem_edit.html")


@app.route("/show_problem/<int:id>")
def view_show_problem(id):
    # print(id)
    return render_template("problem/show_problem.html")


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
    return render_template("user/profile.html")


@app.route("/profile_edit/")
@app.route("/profile_edit/<int:id>")
def view_profile_edit(id=None):
    return render_template("user/profile_edit.html")


@app.route("/contest/<int:contest_id>")
def view_contest(contest_id):
    return render_template("contest/contest.html")


@app.route("/contests/<int:id>")
def view_contest_list(id=None):
    return render_template("contest/contests.html")


@app.route("/contest/<string:name>/problem/<string:problem>")
def view_contest_problem(name, problem):
    return render_template("/contest/problem.html")


@app.route("/contest/edit/<int:id>")
def view_contest_edit(id):
    return render_template("contest/edit.html")


@app.route("/contest/ranklist/<int:id>")
def view_contest_ranklist(id):
    return render_template("contest/ranklist.html")


@app.route("/reset_password/<string:token>")
def view_reset_password(token):
    return render_template("user/reset_password.html")


@app.route("/auth_email/<string:token>")
def view_auth_email(token):
    return render_template("user/auth_email.html")


@app.route("/team")
def view_team_list():
    return render_template("team/team_list.html")


@app.route("/team/<int:id>")
def view_team(id):
    return render_template("team/team.html")


@app.route("/edit_team/<int:id>")
def view_edit_team(id):
    return render_template("team/edit_team.html")


@app.route("/import_from_syzoj")
def view_import_from_syzoj():
    return render_template("import_from_syzoj.html")


@app.route("/help")
def view_help():
    return render_template("help.html")


@app.route("/admin")
def view_admin():
    return render_template("admin.html")


@app.route("/ide")
def view_ide():
    return render_template("ide.html")
