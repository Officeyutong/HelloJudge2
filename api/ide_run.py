from main import db, config, queue


def push_into_queue(code: str, input: str, lang: str) -> str:
    """
    把一个IDE运行请求加入队列
    @param code: 代码
    @param input: 输入文本

    @return: 运行请求ID
    """
    import uuid
    run_id = str(uuid.uuid1())
    queue.send_task("task.ide_run", (lang,
                                     run_id, code, input, {
                                         "compile_time_limit": config.COMPILE_TIME_LIMIT,
                                         "compile_result_length_limit": config.COMPILE_RESULT_LENGTH_LIMIT,
                                         "time_limit": config.IDE_RUN_TIME_LIMIT,
                                         "memory_limit": config.IDE_RUN_MEMORY_LIMIT,
                                         "result_length_limit": config.IDE_RUN_RESULT_LENGTH_LIMIT
                                     }
                                     ))
    return run_id
