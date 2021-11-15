import React, { useState } from "react";
import { useHistory } from "react-router";
import { Button, Checkbox, Form, Header, Input, Message, Segment } from "semantic-ui-react";
import { PUBLIC_URL } from "../App";
import { ButtonClickEvent } from "../common/types";
import { useDocumentTitle, useInputValue } from "../common/Utils";
import utilClient from "./utils/client/UtilClient";

const ImportFromSYZOJ: React.FC<{}> = () => {
    useDocumentTitle("从SYZOJ导入题目");
    const [syzojNG, setSyzojNG] = useState(false);
    const [errorMessage, setErrorMessage] = useState("");
    const [successMessage, setSuccessMessage] = useState("");
    const problemURL = useInputValue("");
    const apiServer = useInputValue("");
    const problemID = useInputValue("");
    const [willPublic, setWillPublic] = useState(false);
    const [openInNewTab, setOpenInNewTab] = useState(false);
    const [message, setMessage] = useState("");
    const history = useHistory();
    const start = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            setMessage("开始导入。请查看服务端后台以获取实时状态。导入完成后将会打开对应题目网页。")
            setErrorMessage("");
            setSuccessMessage("");
            const resp = await (syzojNG ? utilClient.importFromSYZOJNG(apiServer.value, parseInt(problemID.value), willPublic) : utilClient.importFromSYZOJ2(problemURL.value, willPublic));
            setMessage("");
            if (openInNewTab) {
                window.open(`/show_problem/${resp.problem_id}`);
            } else {
                history.push(`${PUBLIC_URL}/show_problem/${resp.problem_id}`);
            }
        } catch { } finally {
            target.classList.remove("loading");
        }
    }
    return <>
        <Header as="h1">
            从SYZOJ导入题目
        </Header>
        <Segment stacked>
            <Form error={errorMessage !== ""} success={successMessage !== ""}>
                <Form.Field>
                    <Checkbox toggle checked={syzojNG} onChange={(_, d) => setSyzojNG(d.checked!)} label="目标网站为SYZOJ-NG站点"></Checkbox>
                </Form.Field>
                {!syzojNG && <Form.Field>
                    <label>SYZOJ题目地址</label>
                    <Input {...problemURL}></Input>
                </Form.Field>}
                {syzojNG && <>
                    <Form.Field>
                        <label>SYZOJ-NG API服务器</label>
                        <Input {...apiServer} placeholder="对于loj.ac，通常应该填写为https://api.loj.ac.cn"></Input>
                    </Form.Field>
                    <Form.Field>
                        <label>SYZOJ-NG 题目ID</label>
                        <Input {...problemID}></Input>
                    </Form.Field>
                </>}
                <Form.Field>
                    <Checkbox toggle checked={willPublic} onChange={(_, d) => setWillPublic(d.checked!)} label="导入后公开"></Checkbox>
                </Form.Field>
                <Form.Field>
                    <Checkbox toggle checked={openInNewTab} onChange={(_, d) => setOpenInNewTab(d.checked!)} label="在新标签页打开"></Checkbox>
                </Form.Field>
                {message !== "" && <Message>
                    <Message.Header>工作中</Message.Header>
                    <Message.Content>{message}</Message.Content>
                </Message>}
                <Message error>
                    <Message.Header>错误</Message.Header>
                    <Message.Content>
                        <p>{errorMessage}</p>
                    </Message.Content>
                </Message>
                <Message error>
                    <Message.Header>成功</Message.Header>
                    <Message.Content>
                        <p>{successMessage}</p>
                    </Message.Content>
                </Message>
                <Message info>
                    <Message.Header>警告</Message.Header>
                    <Message.Content>
                        <p>目前已知问题:</p>
                        <p>1. 仅支持SYZOJ的传统题</p>
                        <p>2. 不支持SYZOJ的附加文件</p>
                        <p>3. 只支持使用testlib的SPJ程序</p>
                        <p>4. 部分子任务的分数可能会出错，请人工核验</p>
                    </Message.Content>
                </Message>
                <Button color="green" onClick={start}>
                    开始
                </Button>
            </Form>
        </Segment>
    </>;
};

export default ImportFromSYZOJ;