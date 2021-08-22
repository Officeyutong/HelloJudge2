import { useState } from "react";
import AceEditor from "react-ace";
import { Button, Form, Input, Message, Modal } from "semantic-ui-react";
import "ace-builds/src-noconflict/mode-javascript";
import _ from "lodash";
import { subtaskToString } from "./SubtasksEdit";
import { ProblemDataProps } from "../ProblemJudgeTab";
import { useAceTheme } from "../../../../../states/StateUtils";
import { useInputValue } from "../../../../../common/Utils";
import { showConfirm, showErrorModal } from "../../../../../dialogs/Dialog";
interface ScriptGeneratrProps {
    files: ProblemDataProps["files"];
    onClose: () => void;
    update: (data: ProblemDataProps["subtasks"]) => void;
};

const GenerateSubtasksWithScript: React.FC<ScriptGeneratrProps> = (props) => {
    const [code, setCode] = useState("");
    const theme = useAceTheme();
    const input = useInputValue("data#.in");
    const output = useInputValue("data#.out");
    const doGenerate = () => {
        const makeInput = (x: any) => input.value.replace("#", x);
        const makeOutput = (x: any) => output.value.replace("#", x);
        try {
            // eslint-disable-next-line no-eval
            const evaled = eval(code);
            if (!(evaled instanceof Array)) {
                showErrorModal("脚本求值结果不是一个数组!");
                return;
            }
            const subtasks: ProblemDataProps["subtasks"] = [];
            const scorePerTask = Math.floor(100 / evaled.length);
            for (const item of evaled) {
                if (!(item instanceof Array)) {
                    showErrorModal("数组中的每一个元素也要是数组");
                    return;
                }
                if (item.length === 0) {
                    showErrorModal("不能有0个测试点的子任务!");
                    return;
                }
                const testcases: ProblemDataProps["subtasks"][0]["testcases"] = [];
                for (const caseid of item) {
                    testcases.push({
                        full_score: 0,
                        input: makeInput(caseid),
                        output: makeOutput(caseid)
                    });
                }
                subtasks.push({
                    name: `Subtask${subtasks.length + 1}`,
                    comment: "",
                    memory_limit: 512,
                    time_limit: 1000,
                    method: "sum",
                    score: scorePerTask,
                    testcases: testcases
                });
            }
            _.last(subtasks)!.score += 100 % evaled.length;
            showConfirm(subtaskToString(subtasks), () => {
                props.update(subtasks);
                props.onClose();
            }, "您确定要使用以下子任务覆盖现有的子任务配置吗?");

        } catch (e) {
            showErrorModal(String(e));
        }
    };
    return <Modal open size="tiny" closeOnDimmerClick={false}>
        <Modal.Header>
            使用脚本生成子任务
        </Modal.Header>
        <Modal.Content>
            <Form>
                <Form.Field>
                    <label>生成脚本</label>
                    <AceEditor
                        value={code}
                        onChange={v => setCode(v)}
                        wrapEnabled
                        theme={theme}
                        mode="javascript"
                        width="100%"
                        height="300px"
                    ></AceEditor>
                </Form.Field>
                <Form.Group widths="equal">
                    <Form.Field>
                        <label>输入文件名</label>
                        <Input {...input}></Input>
                    </Form.Field>
                    <Form.Field>
                        <label>输出文件名</label>
                        <Input {...output}></Input>
                    </Form.Field>
                </Form.Group>
            </Form>
            <Message info>
                <Message.Header>
                    提示
                </Message.Header>
                <Message.Content>
                    <p>可以使用JS的二维数组来快速生成子任务。 例如，指定输入文件名为qwq#.in,而输出文件名为qwq#.out，生成脚本填写以下代码时:</p>
                    <p>[[1,2,3],[2,3,4],[3,4,5]]</p>
                    <p>会自动生成三个子任务，其中第一个子任务包含三个测试点，输入/输出文件分别为(qwq1.in,qwq1.out),(qwq2.in,qwq2.out),(qwq3.in,qwq3.out) 第二个，第三个以此类推。</p>
                    <p>生成脚本可以填写任意可以返回一个合法二维数组的表达式。</p>
                </Message.Content>
            </Message>
        </Modal.Content>
        <Modal.Actions>
            <Button color="green" onClick={doGenerate}>
                生成
            </Button>
            <Button color="red" onClick={props.onClose}>关闭</Button>
        </Modal.Actions>
    </Modal>
};

export default GenerateSubtasksWithScript;