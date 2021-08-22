/**
 * 手机号注册
 * */

import md5 from "md5";
import React, { useState } from "react";
import { useSelector } from "react-redux";
import { Dimmer, Form, Header, Input, Loader, Message, Modal, Segment } from "semantic-ui-react";
import { useDocumentTitle, useInputValue } from "../../common/Utils";
import { showSuccessPopup } from "../../dialogs/Utils";
import { StateType } from "../../states/Manager";
import SendSMSCodeDialog from "../utils/SendSMSCode";
import userClient from "./client/UserClient";

const PhoneRegister: React.FC<{}> = () => {
    const username = useInputValue();
    const email = useInputValue();
    const phone = useInputValue();
    const authcode = useInputValue();
    const password1 = useInputValue();
    const password2 = useInputValue();
    const [errorMessage, setErrorMessage] = useState("");
    const cancelError = () => setErrorMessage("");
    const [sended, setSended] = useState(false);
    const [loading, setLoading] = useState(false);
    const [showingModal, setShowingModal] = useState(false);
    const salt = useSelector((s: StateType) => s.userState.userData.salt);
    const doRegister = async () => {
        if (password1.value !== password2.value) {
            setErrorMessage("两次密码输入不一致");
            return;
        }
        if (authcode.value === "") {
            setErrorMessage("请输入验证码");
            return;
        }
        if (username.value === "" || password1.value === "" || email.value === "") {
            setErrorMessage("请输入用户名或密码或邮箱");
            return;
        }
        try {
            setLoading(true);
            await userClient.doPhoneRegister(username.value, md5(password1.value + salt), email.value, phone.value, authcode.value);
            showSuccessPopup("注册完成，将要跳转");
            setTimeout(() => window.location.href = ("/"), 500);
        } catch {
            setLoading(false);
        }
    };
    const doSendCode = () => {
        if (!/[0-9]{11}/.test(phone.value)) {
            setErrorMessage("请输入合法的11位国内手机号");
            return;
        }
        setShowingModal(true);
    }
    useDocumentTitle("手机号注册");
    return <div>
        <Header as="h1">
            手机号注册
        </Header>
        <Segment stacked style={{ maxWidth: "500px" }}>
            {loading && <Dimmer active>
                <Loader></Loader>
            </Dimmer>}
            <Form error={errorMessage !== ""}>
                <Form.Field>
                    <label>用户名</label>
                    <Input {...username} onClick={cancelError}></Input>
                </Form.Field>
                <Form.Field>
                    <label>邮箱</label>
                    <Input {...email} onClick={cancelError}></Input>
                </Form.Field>
                <Form.Group>
                    <Form.Field>
                        <label>手机号</label>
                        <Input {...phone} onClick={cancelError}></Input>
                    </Form.Field>
                    {sended && <Form.Field>
                        <label>验证码</label>
                        <Input {...authcode} onClick={cancelError}></Input>
                    </Form.Field>}
                </Form.Group>
                <Form.Group>
                    <Form.Field>
                        <label>密码</label>
                        <Input type="password" {...password1} onClick={cancelError}></Input>
                    </Form.Field>
                    <Form.Field>
                        <label>重复密码</label>
                        <Input type="password" {...password2} onClick={cancelError}></Input>
                    </Form.Field>
                </Form.Group>
                <Message>
                    <Message.Header>警告</Message.Header>
                    <Message.Content>
                        <p>1. 手机号为区分不同用户的唯一依据。后期分配题目权限的认定依据也为用户的手机号</p>
                        <p>2. 用户名、手机号、电子邮箱在注册后均无法更改</p>
                        <p>3. 注册后可以在个人信息页面更改密码，或者在登录页面找回密码</p>
                        <p>4. 本页所有项目均为必填</p>
                    </Message.Content>
                </Message>
                <Message error>
                    <Message.Header>错误</Message.Header>
                    <Message.Content>{errorMessage}</Message.Content>
                </Message>
                <Form.Button color="green" onClick={doSendCode}>发送验证码</Form.Button>
                {sended && <Form.Button color="green" onClick={doRegister}>提交</Form.Button>}
            </Form>
        </Segment>
        <Modal open={showingModal}>
            <Modal.Content><SendSMSCodeDialog
                mustNotUse={true}
                onClose={() => { setShowingModal(false); setSended(true) }}
                phone={phone.value}

            ></SendSMSCodeDialog></Modal.Content>
        </Modal>
    </div>;
};

export default PhoneRegister;