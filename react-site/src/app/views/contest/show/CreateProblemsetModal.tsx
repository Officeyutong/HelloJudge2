import React, { useState } from "react";
import { Button, Checkbox, Form, Input, Message, Modal } from "semantic-ui-react";
import { ButtonClickEvent } from "../../../common/types";
import { useInputValue } from "../../../common/Utils";
import problemsetClient from "../../problemset/client/ProblemsetClient";
import contestClient from "../client/ContestClient";
import { v4 as uuidv4 } from "uuid";
import * as clipboard from "clipboardy";
import { showSuccessModal } from "../../../dialogs/Dialog";
interface CreateProblemsetModalProps {
    contest: number;
    onClose: () => void;
    open: boolean;
    title: string;
};

const CreateProblemsetModal: React.FC<CreateProblemsetModalProps> = ({ contest, onClose, open, title }) => {
    const nameEdit = useInputValue(`补题 - ${title}`);
    const [openInNewTab, setOpenInNewTab] = useState(false);
    const submit = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            const { problems } = await contestClient.getContestRawData(contest);
            const id = await problemsetClient.createProblemset();
            await problemsetClient.updateProblemset({
                foreignProblems: [],
                description: "",
                id: id,
                invitationCode: uuidv4(),
                name: nameEdit.value,
                private: 1,
                problems: problems.map(x => x.id),
                showRanklist: 0
            });
            clipboard.write(`${id}`);
            showSuccessModal("操作完成!习题集ID已经复制到剪贴板！");
            if (openInNewTab) window.open(`/problemset/show/${id}`);

        } catch { } finally {
            target.classList.remove("loading");
        }
    };
    return <Modal
        closeOnDimmerClick={false}
        open={open}
    >
        <Modal.Header>快速创建习题集</Modal.Header>
        <Modal.Content>
            <Message info>
                <Message.Header>提示</Message.Header>
                <Message.Content>
                    <p>可以使用此功能直接创建一个由当前比赛的题目所构成的私有习题集，并将其ID复制到剪贴板，供其他用途（比如添加到团队）使用。</p>
                </Message.Content>
            </Message>
            <Form>
                <Form.Field>
                    <label>习题集名称</label>
                    <Input {...nameEdit}></Input>
                </Form.Field>
                <Form.Field>
                    <Checkbox toggle label="创建完成后在新标签页打开" checked={openInNewTab} onChange={(_, d) => setOpenInNewTab(d.checked!)}></Checkbox>
                </Form.Field>
            </Form>
        </Modal.Content>
        <Modal.Actions>
            <Button color="green" onClick={submit}>
                确定
            </Button>
            <Button color="red" onClick={onClose}>
                取消
            </Button>
        </Modal.Actions>
    </Modal>
};

export default CreateProblemsetModal;