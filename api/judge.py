from main import db, config, queue
from models import *
from utils import *
# 把提交加入到评测队列


def push_to_queue(submission_id):
    submit: Submission = db.session.query(
        Submission).filter(Submission.id == submission_id).one()
    submit.judge_result = {
    }
    problem: Problem = db.session.query(Problem).filter(
        Problem.id == submit.problem_id).one()
    # {"subtask1":{"score":100,"status":"WA",testcases:[{"input":"1.in","output":"1.out","score":0,status:"WA","message":""}]}}
    submit.judge_result = dict()
    for item in problem.subtasks:
        submit.judge_result[item["name"]] = {"score": 0,
                                             "status": "waiting",
                                             "testcases": list(map(lambda x: dict(**x, status="waiting", score=0, message="Judging.."), item["testcases"]))
                                             }
    submit.status = "waiting"
    queue.send_task("task.judge", [submit.to_dict()])
    db.session.commit()
# 更新评测状态
def update_status(submission_id, judge_result, judger, message=""):
    """
    更新某个提交测评测状态
    submission_id:int 提交ID
    judge_result:dict 格式同数据模型
    """
    submit: Submission = db.session.query(
        Submission).filter(Submission.id == submission_id).one()
    submit.judge_result = judge_result
    if all(map(lambda x: x["status"] == "accepted"), submit.judge_result.values()):
        submit.status = "accepted"
    elif any(map(lambda x: x["status"] == "judging"), submit.judge_result.values()):
        submit.status = "judging"
    else:
        submit.status = "unaccepted"
    submit.judger = judger
    db.session.commit()
    import flask_socketio
    flask_socketio.emit("update", {
        "judge_result": judge_result,
        "status": submit.status,
        "judger": submit.judger,
        "message": message
    }, room=str(submission_id), namespace="/ws/submission")
