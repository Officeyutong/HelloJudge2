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
        # print(item)
        submit.judge_result[item["name"]] = {"score": 0,
                                             "status": "waiting",
                                             "testcases": list(map(lambda x: dict(**x, status="waiting", score=0, message="Judging..", time_cost=0, memory_cost=0), item["testcases"]))
                                             }

    submit.status = "waiting"
    print(f"Push {submission_id} into queue..")
    queue.send_task("task.judge", [submit.to_dict(), {
                    "compile_time_limit": config.COMPILE_TIME_LIMIT,
                    "compile_result_length_limit": config.COMPILE_RESULT_LENGTH_LIMIT,
                    "spj_execute_time_limit": config.SPJ_EXECUTE_TIME_LIMIT,
                    "extra_compile_parameter": problem.extra_compile_parameter,
                    "auto_sync_files": config.AUTO_SYNC_FILES
                    }])
    # print(f"Push {submission_id} to queue done.")
    db.session.commit()
# 更新评测状态


def update_status(submission_id: int, judge_result: dict, judger: str, message=""):
    """
    更新某个提交测评测状态
    submission_id:int 提交ID
    judge_result:dict 格式同数据模型
    """
    submit: Submission = db.session.query(
        Submission).filter(Submission.id == submission_id).one()
    submit.judge_result = judge_result
    problem: Problem = db.session.query(Problem).filter(
        Problem.id == submit.problem_id).one()
    submit.judger = judger
    submit.message = message
    if submit.get_total_score() == problem.get_total_score():
        submit.status = "accepted"
    elif any(map(lambda x: x["status"] == "waiting", submit.judge_result.values())):
        submit.status = "waiting"
    elif any(map(lambda x: x["status"] == "judging", submit.judge_result.values())):
        submit.status = "judging"
    else:
        submit.status = "unaccepted"
    # print(
    #     f"Update judge status for {submission_id} to {judge_result} ,judger = {judger},message={message}")
    for k, v in submit.judge_result.items():
        v["score"] = int(v["score"])
        for testcase in v["testcases"]:
            testcase["score"] = int(testcase["score"])
    import flask_socketio
    flask_socketio.emit("update", {
        "judge_result": judge_result,
        "status": submit.status,
        "score": submit.get_total_score(),
        "judger": submit.judger,
        "message": message
    }, room="judge:"+str(submission_id), namespace="/ws/submission")
    print(
        f"Submission {submission_id} status updated to \n{judge_result}\nmessage {message},judger {judger}")
    submit.score = submit.get_total_score()
    db.session.commit()
