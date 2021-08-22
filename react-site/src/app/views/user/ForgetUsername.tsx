import React, { useState } from "react";
import { Dimmer, Form, Header, Input, Loader, Message, Modal, Segment } from "semantic-ui-react";
import { useDocumentTitle, useInputValue } from "../../common/Utils";
import { showErrorModal } from "../../dialogs/Dialog";
import { showErrorPopup } from "../../dialogs/Utils";
import SendSMSCodeDialog from "../utils/SendSMSCode";
import userClient from "./client/UserClient";

const ForgetUsername: React.FC<{}> = () => {
    useDocumentTitle("找回用户名");
    const phone = useInputValue();
    const authcode = useInputValue();
    const [codeSended, setCodeSended] = useState(false);
    const [loading, setLoading] = useState(false);
    const [modalShowing, setModalShowing] = useState(false);
    const [successMessage, setSuccessMessage] = useState("");
    const sendRequest = async () => {
        if (phone.value === "") {
            showErrorPopup("请输入手机号!");
            return;
        }
        try {
            const { using } = await userClient.checkPhoneUsing(phone.value);
            if (!using) {
                showErrorModal("该手机号未注册!");
                return;
            }
            setModalShowing(true);
        } catch {

        } finally {
            setLoading(false);
        }
    };
    const requestUsername = async () => {
        if (authcode.value === "") {
            showErrorPopup("请输入验证码!");
            return;
        }
        try {
            const { username } = await userClient.forgetUsername(phone.value, authcode.value);
            setSuccessMessage(`你的用户名为: ${username}`);
        } catch { }
        finally {
            setLoading(false);
        }
    };
    return <div style={{ maxWidth: "500px" }}>
        <Header as="h1">
            找回用户名
        </Header>
        <Segment stacked>
            {loading && <Dimmer>
                <Loader></Loader>
            </Dimmer>}
            <Form success={successMessage !== ""}>
                <Form.Field>
                    <label>手机号</label>
                    <Input {...phone}></Input>
                </Form.Field>
                <Form.Field>
                    <label>验证码</label>
                    <Input {...authcode}></Input>
                </Form.Field>
                <Message success>
                    <Message.Header>
                        查询成功
                    </Message.Header>
                    <Message.Content>
                        <div>{successMessage}</div>
                    </Message.Content>
                </Message>
                <Form.Button color="green" onClick={sendRequest}>发送验证码</Form.Button>
                {codeSended && <Form.Button color="green" onClick={requestUsername}>提交</Form.Button>}
            </Form>
        </Segment>
        <Modal open={modalShowing}>
            <Modal.Content>
                <SendSMSCodeDialog
                    mustNotUse={false}
                    onClose={() => { setModalShowing(false); setCodeSended(true); }}
                    phone={phone.value}
                ></SendSMSCodeDialog>
            </Modal.Content>

        </Modal>
    </div>;
};

export default ForgetUsername;