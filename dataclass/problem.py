from dataclasses import dataclass
from enum import Enum
from typing import List, Mapping


class JudgeMethod(Enum):
    min = "min"
    sum = "sum"


@dataclass
class Example:
    """

    一组样例
    """
    input: str
    output: str


@dataclass
class File:
    name: str
    size: int


@dataclass
class Testcase:
    input: str
    output: str
    full_score: int


@dataclass
class Subtask:
    """
    题目的子任务安排
    """
    # 子任务名
    name: str
    # 子任务分数
    score: int
    # 评测方式
    method: JudgeMethod
    # 时间限制,ms
    time_limit: int
    # 空间限制,MByte
    memory_limit: int
    # 注释
    comment: str
    # 测试点列表
    testcases: List[Testcase]
