/**
 * 邮箱注册
 * */
import md5 from "md5";
import { useState } from "react";
import { useSelector } from "react-redux";
import { Dimmer, Form, Header, Input, Loader, Message, Segment } from "semantic-ui-react";
import { useDocumentTitle, useInputValue } from "../../common/Utils";
import { showErrorModal } from "../../dialogs/Dialog";
import { showSuccessPopup } from "../../dialogs/Utils";
import { StateType } from "../../states/Manager";
import userClient from "./client/UserClient";

const EmailRegister = () => {
    const username = useInputValue();
    const email = useInputValue();
    const password1 = useInputValue();
    const password2 = useInputValue();
    const [loading, setLoading] = useState(false);
    const salt = useSelector((s: StateType) => s.userState.userData.salt);
    const phoneAuth = useSelector((s: StateType) => s.userState.userData.usePhoneAuth);
    if (phoneAuth) {
        window.location.href = "/phone/register";
    }
    const doRegister = async () => {
        if (username.value === "" || email.value === "" || password1.value === "" || password2.value === "") {
            showErrorModal("请输入完整的信息");
            return;
        }
        if (password1.value !== password2.value) {
            showErrorModal("两次密码不匹配");
            return;
        }
        try {
            setLoading(true);
            await userClient.doEmailRegister(username.value, md5(password1.value + salt), email.value);
            showSuccessPopup("注册成功，即将跳转");
            setTimeout(() => window.location.href = ("/"), 500);
        } catch (e) {
        } finally { setLoading(false); }
    };
    useDocumentTitle("邮箱注册");
    return <div>
        <Header as="h1">
            注册
        </Header>
        <Segment stacked style={{ maxWidth: "70%" }}>
            {loading && <Dimmer active><Loader></Loader></Dimmer>}
            <Form>
                <Form.Field>
                    <label>用户名</label>
                    <Input {...username} ></Input>
                </Form.Field>
                <Form.Field>
                    <label>邮箱</label>
                    <Input {...email} ></Input>
                </Form.Field>
                <Form.Group>
                    <Form.Field>
                        <label>密码</label>
                        <Input type="password" {...password1} ></Input>
                    </Form.Field>
                    <Form.Field>
                        <label>重复密码</label>
                        <Input type="password" {...password2} ></Input>
                    </Form.Field>
                </Form.Group>
                <Message>
                    <Message.Header>警告</Message.Header>
                    <Message.Content>
                        <p>用户名和邮箱在注册后无法更改</p>
                    </Message.Content>
                </Message>
                <Form.Button color="green" onClick={doRegister}>注册</Form.Button>
            </Form>
        </Segment>
    </div>;
};

export default EmailRegister;