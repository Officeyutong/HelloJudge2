import _ from "lodash";
import React, { Fragment, useState } from "react";
import { Button, Divider, Form, Header, Input, Segment } from "semantic-ui-react";
import { KeyDownEvent } from "../../../../../common/types";
import { showConfirm } from "../../../../../dialogs/Dialog";
import { ProblemDataProps } from "../ProblemJudgeTab";
import generateSubtasks from "./GenerateSubtasks";
import GenerateSubtasksWithScript from "./GenerateSubtasksWithScript";
import SubtaskConfigEdit from "./SubtaskConfigEdit";
import SubtaskEntryEdit from "./SubtaskEntryEdit";
type SubtaskType = ProblemDataProps["subtasks"];
interface SubtasksEditProps {
    subtasks: SubtaskType;
    files: ProblemDataProps["files"];
    onUpdate: (d: SubtaskType) => void;
};

const subtaskToString = (d: SubtaskType): string => {
    const buf: string[] = [];
    for (const item of d) {
        buf.push(item.name, ": ");
        buf.push(item.testcases.map(testcase => `<${testcase.input},${testcase.output}> `).join(", "));
        buf.push(",");
    }
    return buf.join("");
};

const subtaskToReactNode = (d: SubtaskType): React.ReactNode => {
    return <div>
        {d.map((x, i) => <div key={i}>
            <span style={{ fontWeight: "bold" }}>{x.name}: </span>
            {x.testcases.map(y => `<${y.input}, ${y.output}>`).join(",")}
        </div>)}
    </div>
};

const SubtaskEdit: React.FC<SubtasksEditProps> = (props) => {
    const { subtasks: data, onUpdate, files } = props;
    const update = onUpdate;
    const [showScriptModal, setShowScriptModal] = useState(false);
    const [showConfigModal, setShowConfigModal] = useState(false);
    const generateWithScript = () => {
        setShowScriptModal(true);
    };
    const autoGenerateSubtask = () => {
        const subtasks = generateSubtasks(files);
        showConfirm(subtaskToString(subtasks), () => {
            update(subtasks);
        }, "您确定要生成以下子任务吗? (这一操作会清空已有的子任务配置)");
    }
    return <>
        <Header as="h3">
            子任务设定
        </Header>
        <Segment>
            <Form as="div">
                <Form.Group>
                    <Form.Field>
                        <label>统一修改时限(毫秒)</label>
                        <Input onKeyDown={(evt: KeyDownEvent) => {
                            if (evt.key !== "Enter") return;
                            const content = evt.currentTarget.value;
                            update(data.map(x => ({ ...x, time_limit: parseInt(content) })));
                        }} placeholder="按回车键应用"></Input>
                    </Form.Field>
                    <Form.Field>
                        <label>统一修改内存限制(MB)</label>
                        <Input onKeyDown={(evt: KeyDownEvent) => {
                            if (evt.key !== "Enter") return;
                            const content = evt.currentTarget.value;
                            update(data.map(x => ({ ...x, memory_limit: parseInt(content) })));
                        }} placeholder="按回车键应用"></Input>
                    </Form.Field>
                    <Form.Field>
                        <label>操作</label>
                        <Button onClick={autoGenerateSubtask} color="green">自动生成子任务</Button>
                        <Button onClick={generateWithScript} color="green">使用脚本生成子任务</Button>
                        <Button onClick={() => setShowConfigModal(true)} color="green">
                            直接编辑配置文件
                        </Button>
                    </Form.Field>
                </Form.Group>
            </Form>
            <Divider></Divider>
            {data.map((x, i) => <Fragment key={i}>
                <SubtaskEntryEdit key={i}
                    files={files}
                    onUpdate={d => update(_.set([...data], i, d))}
                    subtask={x}

                ></SubtaskEntryEdit>
                <Button color="red" onClick={() => update(data.filter((y, j) => j !== i))} style={{ marginTop: "10px" }}>
                    删除该子任务
                </Button>
                <Divider></Divider>
            </Fragment>)}
            <Button onClick={() => update([...data, {
                comment: "",
                memory_limit: 512,
                method: "sum",
                name: "新建子任务",
                score: 100 - _.sum(data.map(x => x.score)),
                testcases: [],
                time_limit: 1000
            }])} color="green">
                添加子任务
            </Button>
        </Segment>
        {showScriptModal && <GenerateSubtasksWithScript
            files={files}
            onClose={() => setShowScriptModal(false)}
            update={d => update(d)}
        ></GenerateSubtasksWithScript>}
        {showConfigModal && <SubtaskConfigEdit
            config={data}
            files={files}
            onClose={() => setShowConfigModal(false)}
            onUpdate={d => update(d)}
        ></SubtaskConfigEdit>}
    </>;
};

export default React.memo(SubtaskEdit, (prev, next) => {
    return prev.files === next.files && prev.subtasks === next.subtasks;
});

export {
    subtaskToString,
    subtaskToReactNode
};