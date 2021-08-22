from main import web_app as app
from main import config, csrf
from flask import render_template, redirect
from urllib.parse import quote


@app.context_processor
def consts():
    return {
        "DEBUG": config.DEBUG,
        "APP_NAME": config.APP_NAME,
        "SALT": config.PASSWORD_SALT,
        "USING_CSRF_TOKEN": config.ENABLE_CSRF_TOKEN,
    }


@app.errorhandler(404)
def handler_404(exc):
    return redirect(f"/error?message={quote(f'页面未找到!')}&title={quote('404')}")


@app.route("/")
def view_index():
    return render_template("main.html")


# @app.route("/login")
# def view_login():
#     return render_template("user/login.html")


# @app.route("/phone/register")
# def view_register_phone():
#     return render_template("user/register_phone.html")


# @app.route("/register")
# def view_register():
#     return render_template("user/register.html")


@app.route("/ranklist/<int:id>")
def view_global_ranklist(id):
    return render_template("ranklist.html")


# @app.route("/problems")
# @app.route("/problems/<int:id>")
# def view_problems(id=-1):
#     return render_template("problem/problems.html")


@app.route("/submissions")
@app.route("/submissions/<int:id>")
def view_submissions(id=-1):
    return render_template("submissions.html")


@app.route("/discussions/<string:path>/<int:page>")
def view_discussions(path, page):
    return render_template("discussions.html")


# @app.route("/problem_edit/<int:id>")
# def view_edit_problem(id):
#     # print(id)
#     return render_template("problem/problem_edit.html")


# @app.route("/show_problem/<int:id>")
# def view_show_problem(id):
#     # print(id)
#     return render_template("problem/show_problem.html")


@app.route("/show_submission/<int:id>")
def view_show_submission(id):
    # print(id)
    return render_template("show_submission.html")


@app.route("/show_discussion/<int:id>")
def view_show_discussion(id):
    # print(id)
    return render_template("show_discussion.html")


# @app.route("/profile/<int:id>")
# def view_profile(id):
#     return render_template("user/profile.html")


# @app.route("/profile_edit/")
# @app.route("/profile_edit/<int:id>")
# def view_profile_edit(id=None):
#     return render_template("user/profile_edit.html")


# @app.route("/contest/<int:contest_id>")
# def view_contest(contest_id):
#     return render_template("contest/contest.html")


# @app.route("/contests/<int:id>")
# def view_contest_list(id=None):
#     return render_template("contest/contests.html")


@app.route("/contest/<string:name>/problem/<string:problem>")
def view_contest_problem(name, problem):
    return render_template("/contest/problem.html")


# @app.route("/contest/edit/<int:id>")
# def view_contest_edit(id):
#     return render_template("contest/edit.html")


# @app.route("/contest/ranklist/<int:id>")
# def view_contest_ranklist(id):
#     return render_template("contest/ranklist.html")


# @app.route("/reset_password/<string:token>")
# def view_reset_password(token):
#     return render_template("user/reset_password.html")


# @app.route("/phone/reset_password")
# def view_phone_reset_password():
#     return render_template("user/reset_password_phone.html")


# @app.route("/auth_email/<string:token>")
# def view_auth_email(token):
#     return render_template("user/auth_email.html")


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


# @app.route("/admin")
# def view_admin():
#     return render_template("admin.html")


@app.route("/ide")
def view_ide():
    return render_template("ide.html")


# @app.route("/remote_judge/accounts")
# def view_remote_judge_accounts():
#     return render_template("remote_judge/accounts.html")


# @app.route("/remote_judge/add_problem")
# def view_remote_judge_add_problem():
#     return render_template("remote_judge/add_problem.html")


# @app.route("/remote_judge/show_problem/<string:id>")
# def view_remote_judge_show_problem(id):
#     return render_template("remote_judge/show_problem.html")


# @app.route("/problemset/list")
# @app.route("/problemset/list/")
# @app.route("/problemset/list/<int:page>")
# def view_problemset_list(page: int = -1):
#     return render_template("problemset/list.html")


# @app.route("/problemset/show/<int:id>")
# def view_problemset_show(id: int = -1):
#     return render_template("problemset/show.html")


# @app.route("/problemset/edit/<int:id>")
# def view_problemset_edit(id: int = -1):
#     return render_template("problemset/edit.html")


@app.route("/challenge/list")
def view_challenge_list():
    return render_template("/challenge/list.html")


@app.route("/challenge/edit/<int:id>")
def view_challenge_edit(id: int):
    return render_template("/challenge/edit.html")


@app.route("/error")
def view_error_page():
    return render_template("error.html")


@app.route("/success")
def view_success_page():
    return render_template("success.html")


@app.route("/card/problem/<int:id>")
def view_problem_card(id: int):
    return render_template("card/problem.html")


@app.route("/card/sendsms")
def view_sendsms_card():
    return render_template("card/send_smscode.html")


# @app.route("/phoneauth")
# def view_phoneauth():
#     return render_template("phoneauth.html")


# @app.route("/tags/edit")
# def view_tags_edit():
#     return render_template("tags_edit.html")


# @app.route("/tags_edit/<int:id>")
# def view_problem_tags_edit(id: int):
#     return render_template("problem/tags.html")


# @app.route("/permissionpack/list")
# def view_permissionpack_list():
#     return render_template("permissionpack/list.html")


# @app.route("/permissionpack/edit/<int:id>")
# def view_permissionpack_edit(id):
#     return render_template("permissionpack/edit.html")


# @app.route("/permissionpack/use")
# def view_permissionpack_use(id):
#     return render_template("permissionpack/use.html")


# @app.route("/permissionpack/user_packs")
# def view_permissionpack_user_packs():
#     return render_template("permissionpack/user_packs.html")


@app.route("/problemtodo/list")
def problemtodo_list():
    return render_template("problemtodo/list.html")


# @app.route("/virtualcontest/create/<int:id>")
# def virtualcontest_create(id):
#     return render_template("virtualcontest/create.html")


# @app.route("/virtualcontest/list")
# def virtualcontest_list():
#     return render_template("virtualcontest/list.html")


@app.route("/blog/list/<int:id>")
def blog_list(id: int = 1):
    return render_template("blog/list.html")


@app.route("/blog/edit/")
@app.route("/blog/edit/<int:id>")
def blog_edit(id: int = 1):
    return render_template("blog/edit.html")


@app.route("/wiki/config")
def wiki_config():
    return render_template("wiki/config.html")


@app.route("/wiki/<int:id>")
@app.route("/wiki/")
def wiki_page(id=-1):
    return render_template("wiki/page.html")


@app.route("/wiki/edit/<int:id>")
@app.route("/wiki/edit")
def wiki_edit(id=-1):
    return render_template("wiki/edit.html")


@app.route("/wiki/versions/<int:id>")
def wiki_versions(id=-1):
    return render_template("wiki/versions.html")


@app.route("/submit_answer/<int:id>")
def submit_answer(id: int):
    return render_template("submit_answer.html")


# @app.route("/contest/clarification/edit/<int:id>")
# def view_clarification_edit(id: int):
#     return render_template("contest/clarification_edit.html")
