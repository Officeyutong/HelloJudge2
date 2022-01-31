import React from "react";
import { Dropdown, Form, Header } from "semantic-ui-react";
import { ScoringMethodMapping, SubtaskEntry, SubtaskScoringMethod } from "../../../client/types";
import { ProblemDataProps } from "../ProblemJudgeTab";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-markdown";
import { useAceTheme } from "../../../../../states/StateUtils";
import TestcaseTable from "./TestcaseTable";
interface SubtaskEntryEditProps {
    subtask: SubtaskEntry;
    files: ProblemDataProps["files"];
    onUpdate: (d: SubtaskEntry) => void;
};



const SubtaskEntryEdit: React.FC<SubtaskEntryEditProps> = (props) => {
    const {
        subtask, files
    } = props;
    const update = props.onUpdate;

    const theme = useAceTheme();
    return <>
        <Header as="h2">
            {subtask.name}
        </Header>
        <Form widths="equal">
            <Form.Group widths="equal">
                <Form.Input label="子任务名" value={subtask.name} onChange={(_, d) => update({ ...subtask, name: d.value })}></Form.Input>
                <Form.Input label="时间限制(ms)" value={subtask.time_limit} onChange={(_, d) => update({ ...subtask, time_limit: parseInt(d.value) })}></Form.Input>
                <Form.Input label="内存限制" value={subtask.memory_limit} onChange={(_, d) => update({ ...subtask, memory_limit: parseInt(d.value) })}></Form.Input>
            </Form.Group>
            <Form.Group widths="equal">
                <Form.Field>
                    <label>评分方式</label>
                    <Dropdown
                        text={ScoringMethodMapping[subtask.method]}
                        options={[
                            { value: "min", text: ScoringMethodMapping["min"] },
                            { value: "sum", text: ScoringMethodMapping["sum"] },
                        ]}
                        fluid
                        selection
                        onChange={(_, d) => update({ ...subtask, method: d.value as SubtaskScoringMethod })}
                    >
                    </Dropdown>
                </Form.Field>
                <Form.Input label="子任务总分" value={subtask.score} onChange={(_, d) => update({ ...subtask, score: parseInt(d.value) })}></Form.Input>
            </Form.Group>
            <Form.Field>
                <label>注释</label>
                <AceEditor
                    value={subtask.comment}
                    theme={theme}
                    width="100%"
                    height="100px"
                    onChange={v => update({ ...subtask, comment: v })}
                ></AceEditor>
            </Form.Field>
            <Form.Field>
                <label>测试点</label>
                <TestcaseTable
                    files={files}
                    onUpdate={d => update({ ...subtask, testcases: d })}
                    testcases={subtask.testcases}
                ></TestcaseTable>
            </Form.Field>
        </Form>
    </>
};

export default SubtaskEntryEdit;