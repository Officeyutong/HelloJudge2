import json
from dataclasses import dataclass
from typing import List, Mapping
@dataclass
class TestcaseResult:
    """
    一个测试点的评测结果

    """
    # 输入文件名
    input: str
    # 输出文件名
    output: str
    # 测试点得分
    score: int
    # 测试点状态
    status: str
    # 附加信息
    message: str
    # 测试点得分，对于取min情况只有0或1
    full_score: int


@dataclass
class SubtaskResult:
    """
    一个子任务的评测结果

    """
    # 子任务得分
    score: int
    # 子任务状态
    status: str
    # 测试点
    testcases: List[TestcaseResult]

