import React from "react";
import { useState } from "react";
import { Button, Form } from "semantic-ui-react";
import JudgeStatusLabel from "../../utils/JudgeStatusLabel";
import { SubmissionFilter } from "../client/types";

interface SubmissionFilterProps {
    defaultFilter: SubmissionFilter;
    onUpdate: (d: SubmissionFilter) => void;
};
type ExtraSubmissionFilter = Required<{ [K in keyof SubmissionFilter]: { used: boolean, value?: Required<SubmissionFilter>[K] } }>;
const FILTERABLE_STATUS: ("accepted" | "unaccepted" | "judging" | "waiting" | "compile_error")[] = ["accepted", "unaccepted", "judging", "waiting", "compile_error"];
const SubmissionFilterArea: React.FC<SubmissionFilterProps> = ({
    defaultFilter,
    onUpdate
}) => {
    const [filter, setFilter] = useState<ExtraSubmissionFilter>({
        contest: { used: defaultFilter.contest !== undefined, value: defaultFilter.contest || -1 },
        max_score: { used: defaultFilter.max_score !== undefined, value: defaultFilter.max_score || 100 },
        min_score: { used: defaultFilter.min_score !== undefined, value: defaultFilter.min_score || 0 },
        problem: { used: defaultFilter.problem !== undefined, value: defaultFilter.problem || 1 },
        status: { used: defaultFilter.status !== undefined, value: defaultFilter.status || "accepted" },
        uid: { used: defaultFilter.uid !== undefined, value: defaultFilter.uid }
    });
    return <>
        <Form>
            <Form.Checkbox toggle checked={filter.uid.used} onClick={(e, d) => {
                if (filter.uid.used) setFilter({ ...filter, uid: { used: false, value: filter.uid.value } });
                else setFilter({ ...filter, uid: { used: true, value: filter.uid.value } })
            }}
                label="筛选用户名/UID"
            ></Form.Checkbox>
            {filter.uid.used && <Form.Input fluid={false} label="用户名" type="text" value={filter.uid.value || ""} onChange={(e, d) => setFilter({ ...filter, uid: { used: true, value: d.value } })}></Form.Input>}

            <Form.Checkbox toggle checked={filter.problem.used} onClick={(e, d) => {
                if (filter.problem.used) setFilter({ ...filter, problem: { used: false, value: filter.problem.value } });
                else setFilter({ ...filter, problem: { used: true, value: filter.problem.value } })
            }}
                label="筛选题目"
            ></Form.Checkbox>
            {filter.problem.used && <Form.Input fluid={false} label="题目ID" type="number" value={filter.problem.value || 1} onChange={(e, d) => setFilter({ ...filter, problem: { used: true, value: parseInt(d.value) } })}></Form.Input>}

            <Form.Checkbox toggle checked={filter.status.used} onClick={(e, d) => {
                if (filter.status.used) setFilter({ ...filter, status: { used: false, value: filter.status.value } });
                else setFilter({ ...filter, status: { used: true, value: filter.status.value } })
            }}
                label="筛选提交状态"
            ></Form.Checkbox>
            {filter.status.used && <Form.Dropdown
                label="提交状态"
                selection
                options={FILTERABLE_STATUS.map((x, j) => ({
                    text: x,
                    key: j,
                    value: x,
                    content: <JudgeStatusLabel status={x}></JudgeStatusLabel>, onClick: (e, d) =>
                        setFilter({ ...filter, status: { used: true, value: x } })
                }))}
                fluid
                value={filter.status.value}
            >
            </Form.Dropdown>}
            <Form.Checkbox toggle checked={filter.min_score.used} onClick={(e, d) => {
                if (filter.min_score.used) setFilter({ ...filter, min_score: { used: false, value: filter.min_score.value } });
                else setFilter({ ...filter, min_score: { used: true, value: filter.min_score.value } })
            }}
                label="筛选最低分"
            ></Form.Checkbox>
            {filter.min_score.used && <Form.Input fluid={false} label="最低分" type="number" value={filter.min_score.value} onChange={(e, d) => setFilter({ ...filter, min_score: { used: true, value: parseInt(d.value) } })}></Form.Input>}
            <Form.Checkbox toggle checked={filter.max_score.used} onClick={(e, d) => {
                if (filter.max_score.used) setFilter({ ...filter, max_score: { used: false, value: filter.max_score.value } });
                else setFilter({ ...filter, max_score: { used: true, value: filter.max_score.value } })
            }}
                label="筛选最高分"
            ></Form.Checkbox>
            {filter.max_score.used && <Form.Input fluid={false} label="最高分" type="number" value={filter.max_score.value} onChange={(e, d) => setFilter({ ...filter, max_score: { used: true, value: parseInt(d.value) } })}></Form.Input>}
            <Form.Checkbox toggle checked={filter.contest.used} onClick={(e, d) => {
                if (filter.contest.used) setFilter({ ...filter, contest: { used: false, value: filter.contest.value } });
                else setFilter({ ...filter, contest: { used: true, value: filter.contest.value } })
            }}
                label="筛选比赛"
            ></Form.Checkbox>
            {filter.contest.used && <Form.Input fluid={false} label="比赛" type="number" value={filter.contest.value} onChange={(e, d) => setFilter({ ...filter, contest: { used: true, value: parseInt(d.value) } })}></Form.Input>}
            <Button size="tiny" color="green" onClick={() => onUpdate(Object.fromEntries(Object.entries(filter).filter(x => x[1].used).map(x => ([x[0], x[1].used ? x[1].value : undefined]))))}>
                应用更改
            </Button>
        </Form>
    </>;
};

export default React.memo(SubmissionFilterArea, (prev, next) => prev.defaultFilter === next.defaultFilter);