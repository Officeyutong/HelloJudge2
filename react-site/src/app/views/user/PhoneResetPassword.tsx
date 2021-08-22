import md5 from "md5";
import React, { useState } from "react";
import { Dimmer, Form, Header, Input, Loader, Modal, Segment } from "semantic-ui-react";
import { useDocumentTitle, useInputValue, usePasswordSalt } from "../../common/Utils";
import { showErrorModal } from "../../dialogs/Dialog";
import { showSuccessPopup } from "../../dialogs/Utils";
import SendSMSCodeDialog from "../utils/SendSMSCode";
import userClient from "./client/UserClient";

const PhoneResetPassword: React.FC<{}> = () => {
    useDocumentTitle("手机号重置密码");
    const phone = useInputValue();
    const password = useInputValue();
    const authcode = useInputValue();
    const salt = usePasswordSalt();
    const [codeSended, setCodeSended] = useState(false);
    const [loading, setLoading] = useState(false);
    const [modalShowing, setModalShowing] = useState(false);
    const doResetPassword = async () => {
        if (password.value === "" || authcode.value === "") {
            showErrorModal("请输入密码或验证码");
            return;
        }
        try {
            setLoading(true);
            await userClient.doPhoneResetPassword(phone.value, md5(password.value + salt), authcode.value);
            showSuccessPopup("操作完成，正在跳转");
            setTimeout(() => window.location.href = "/login", 500);
        } catch {
            setLoading(false);
        }

    };
    const doSendCode = async () => {
        if (!/[0-9]{11}/.test(phone.value)) {
            showErrorModal("请输入合法的11位国内手机号");
            return;
        }
        try {
            setLoading(true);
            if (!(await userClient.checkPhoneUsing(phone.value)).using) {
                showErrorModal("该手机号未注册");
                return;
            }
            setModalShowing(true);
        } catch { } finally {
            setLoading(false);
        }
    };
    return <div style={{ maxWidth: "500px" }}>
        <Header as="h1">
            重置密码
        </Header>
        <Segment stacked>
            {loading && <Dimmer>
                <Loader></Loader>
            </Dimmer>}
            <Form>
                <Form.Field>
                    <label>手机号</label>
                    <Input {...phone}></Input>
                </Form.Field>
                <Form.Field>
                    <label>新密码</label>
                    <Input {...password}></Input>
                </Form.Field>
                <Form.Field>
                    <label>验证码</label>
                    <Input {...authcode}></Input>
                </Form.Field>
                <Form.Button color="green" onClick={doSendCode}>发送验证码</Form.Button>
                {codeSended && <Form.Button color="green" onClick={doResetPassword}>提交</Form.Button>}
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

export default PhoneResetPassword;