import pymysql
import migrate_config
from main import db
from typing import Dict, List
import models
import json
import uuid


def main():
    conn = pymysql.connect(
        host=migrate_config.OLD_HOST,
        port=migrate_config.OLD_PORT,
        user=migrate_config.OLD_USER,
        password=migrate_config.OLD_PASSWORD,
        db=migrate_config.OLD_DATABASE
    )
    joined_teams: Dict[int, List[int]] = {}
    user_admin_teams: Dict[int, List[int]] = {}
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM users")
    print("loading user...")
    for item in cursor.fetchall():
        joined_teams[item["id"]] = json.loads(item["joined_teams"])
        print(item["username"])
        user = models.User(
            id=item["id"],
            banned=item["banned"],
            username=item["username"],
            password=item["password"],
            description=item["description"],
            email=item["email"],
            register_time=item["register_time"],
            rating_history=json.loads(item["rating_history"]),
            rating=item["rating"],
            permission_group=item["permission_group"],
            permissions=json.loads(item["permissions"]),
            force_logout_before=item["force_logout_before"],
            phone_number=None,
            phone_verified=False
        )
        db.session.add(user)
    db.session.commit()
    print("loading problems...")
    cursor.execute("SELECT * FROM problems")
    for item in cursor.fetchall():
        print(item["id"], item["title"])
        prob = models.Problem(
            id=item["id"],
            uploader_id=item["uploader_id"],
            title=item["title"],
            background=item["background"],
            content=item["content"],
            input_format=item["input_format"],
            output_format=item["output_format"],
            hint=item["hint"],
            example=json.loads(item["example"]),
            files=json.loads(item["files"]),
            downloads=json.loads(item["downloads"]),
            provides=json.loads(item["provides"]),
            subtasks=json.loads(item["subtasks"]),
            public=item["public"],
            spj_filename=item["spj_filename"],
            using_file_io=item["using_file_io"],
            input_file_name=item["input_file_name"],
            output_file_name=item["output_file_name"],
            problem_type=item["problem_type"],
            can_see_results=item["can_see_results"],
            create_time=item["create_time"],
            extra_parameter=json.loads(item["extra_parameter"]),
            remote_judge_oj=item["remote_judge_oj"],
            remote_problem_id=item["remote_problem_id"],
            cached_submit_count=0,
            cached_accepted_count=0,
            team_id=None,
            invite_code=str(uuid.uuid1()),
            submission_visible=True
        )
        db.session.add(prob)
    db.session.commit()
    print("loading submissions...")
    cursor.execute("SELECT * FROM submissions")
    for item in cursor.fetchall():
        print(item["id"])
        item.update(dict(judge_result=json.loads(item["judge_result"]),
                         selected_compile_parameters=json.loads(
                    item["selected_compile_parameters"])))
        submission = models.Submission(
            **item
        )
        db.session.add(submission)
    db.session.commit()
    print("loading contests..")
    cursor.execute("SELECT * FROM contest")
    for item in cursor.fetchall():
        print(item["id"])
        item.update(dict(closed=False,
                       problems=json.loads(item["problems"])))
        contest = models.Contest(
            **item
        )
        db.session.add(contest)
    db.session.commit()
    print("loading teams..")
    cursor.execute("SELECT * FROM team")
    for item in cursor.fetchall():
        team = models.Team(
            id=item["id"],
            name=item["name"],
            description=item["description"],
            owner_id=item["owner_id"],
            tasks=json.loads(item["tasks"]),
            create_time=item["create_time"],
            invite_code=str(uuid.uuid1()),
            private=False,
            team_contests=[],
            team_problems=[],
            team_problemsets=[]
        )
        for uid in item["admins"]:
            if uid not in user_admin_teams:
                user_admin_teams[uid] = []
            user_admin_teams[uid].append(item["id"])
        db.session.add(team)
    db.session.commit()
    for user, teams in joined_teams.items():
        admin_teams = user_admin_teams.get(user, set())
        for x in teams:
            db.session.add(models.TeamMember(
                uid=user,
                team_id=x,
                is_admin=x in admin_teams
            ))
    db.session.commit()
    print("loading permission groups..")
    db.session.query(models.PermissionGroup).delete()
    db.session.commit()
    cursor.execute("SELECT * FROM permission_groups")
    for item in cursor.fetchall():
        item.update(dict(permissions=json.loads(item["permissions"])))
        db.session.add(models.PermissionGroup(
            **item
        ))
    db.session.commit()
    print("loading problemsets...")
    cursor.execute("SELECT * FROM problem_set")
    for item in cursor.fetchall():
        item.update(dict(problems=json.loads(item["problems"])))
        db.session.add(models.ProblemSet(
            **item
        ))
    db.session.commit()
    print("loading remote accounts...")
    cursor.execute("SELECT * FROM remote_accounts")
    for item in cursor.fetchall():
        item.update(dict(session=item["session"]))
        db.session.add(models.RemoteAccount(
            **item
        ))
    db.session.commit()
    print("loading discussions..")
    cursor.execute("SELECT * FROM discussions")
    for item in cursor.fetchall():
        db.session.add(models.Discussion(**item, private=False))
    db.session.commit()
    print("loading comments..")
    cursor.execute("SELECT * FROM comments")
    for item in cursor.fetchall():
        if not db.session.query(models.Discussion).filter_by(id=item["discussion_id"]).count():
            continue
        db.session.add(models.Comment(**item))
    db.session.commit()
    print("Done!")


if __name__ == "__main__":
    main()
