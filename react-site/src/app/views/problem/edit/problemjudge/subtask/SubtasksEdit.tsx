import _ from "lodash";
import React, { Fragment, useCallback, useEffect, useRef, useState } from "react";
import { Button, Divider, Form, Header, Input, Segment } from "semantic-ui-react";
import { KeyDownEvent } from "../../../../../common/types";
import { showConfirm } from "../../../../../dialogs/Dialog";
import { SubtaskEntry } from "../../../client/types";
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
// let arr: any[] = [];
// (window as any).arr = arr;
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

type ActionType = { type: "modify"; index: number; data: SubtaskEntry } |
{ type: "append"; data: SubtaskEntry } |
{ type: "remove"; index: number };

const SubtaskEdit: React.FC<SubtasksEditProps> = (props) => {
    const { onUpdate, files, subtasks: _subtasks } = props;
    // console.log("init data", props.subtasks);
    // const update = (d: SubtaskType) => {
    //     onUpdate(d);
    // };
    const dataRef = useRef<typeof _subtasks>(props.subtasks);
    useEffect(() => { dataRef.current = props.subtasks; }, [props.subtasks]);
    const applyAction = useCallback((action: ActionType) => {
        switch (action.type) {
            case "append":
                onUpdate([...dataRef.current, action.data]);
                break;
            case "modify":
                onUpdate(_.set([...dataRef.current], action.index, action.data));
                break;
            case "remove":
                onUpdate(dataRef.current.filter((_, j) => j !== action.index));
        }
    }, [onUpdate]);

    const [showScriptModal, setShowScriptModal] = useState(false);
    const [showConfigModal, setShowConfigModal] = useState(false);
    const generateWithScript = () => {
        setShowScriptModal(true);
    };
    const autoGenerateSubtask = () => {
        const subtasks = generateSubtasks(files);
        showConfirm(subtaskToString(subtasks), () => {
            props.onUpdate(subtasks);
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
                            props.onUpdate(props.subtasks.map(x => ({ ...x, time_limit: parseInt(content) })));
                        }} placeholder="按回车键应用"></Input>
                    </Form.Field>
                    <Form.Field>
                        <label>统一修改内存限制(MB)</label>
                        <Input onKeyDown={(evt: KeyDownEvent) => {
                            if (evt.key !== "Enter") return;
                            const content = evt.currentTarget.value;
                            props.onUpdate(props.subtasks.map(x => ({ ...x, memory_limit: parseInt(content) })));
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
            {props.subtasks.map((x, i) => <Fragment key={i}>
                {/* {console.log("binding data",data)} */}
                <SubtaskEntryEdit
                    files={files}
                    onUpdate={d => {
                        applyAction({ type: "modify", index: i, data: d });
                        // arr.push(applyAction);
                        // console.log(applyAction);
                    }}
                    subtask={x}

                ></SubtaskEntryEdit>
                <Button color="red" onClick={() => applyAction({ type: "remove", index: i })} style={{ marginTop: "10px" }}>
                    删除该子任务
                </Button>
                <Divider></Divider>
            </Fragment>)}
            <Button onClick={() => applyAction({
                type: "append", data: {
                    comment: "",
                    memory_limit: 512,
                    method: "sum",
                    name: "新建子任务",
                    score: 100 - _.sum(props.subtasks.map(x => x.score)),
                    testcases: [],
                    time_limit: 1000
                }
            })} color="green">
                添加子任务
            </Button>
        </Segment>
        {showScriptModal && <GenerateSubtasksWithScript
            files={files}
            onClose={() => setShowScriptModal(false)}
            update={d => props.onUpdate(d)}
        ></GenerateSubtasksWithScript>}
        {showConfigModal && <SubtaskConfigEdit
            config={props.subtasks}
            files={files}
            onClose={() => setShowConfigModal(false)}
            onUpdate={d => props.onUpdate(d)}
        ></SubtaskConfigEdit>}
    </>;
};

export default SubtaskEdit;

export {
    subtaskToString,
    subtaskToReactNode
};