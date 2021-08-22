/**
 * 邮箱注册重置密码（输入新密码）
 * 
 * 
 * */
import md5 from "md5";
import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { Dimmer, Form, Header, Input, Loader, Segment } from "semantic-ui-react";
import { useDocumentTitle, useInputValue, usePasswordSalt } from "../../common/Utils";
import { showSuccessPopup } from "../../dialogs/Utils";
import userClient from "./client/UserClient";

const EmailResetPasswordView: React.FC<{}> = () => {

    const params = useParams<{ token: string }>();
    const token = decodeURIComponent(decodeURIComponent(params.token));
    const identifier = useInputValue();
    const password = useInputValue();
    const [loading, setLoading] = useState(false);
    const salt = usePasswordSalt();
    useDocumentTitle("重置密码");
    const doReset = async () => {
        try {
            setLoading(true);
            await userClient.doEmailResetPassword(identifier.value, md5(password.value + salt), token);
            showSuccessPopup("重置成功，即将跳转");
            setTimeout(() => window.location.href = "/login", 500);
        } catch {

        } finally {
            setLoading(true);
        }
    }
    return <div style={{ maxWidth: "500px" }}>
        <Header as="h1">
            重置密码
        </Header>
        <Segment stacked>
            {loading && <Dimmer active>
                <Loader></Loader>
            </Dimmer>}
            <Form>
                <Form.Field>
                    <label>用户名或邮箱</label>
                    <Input {...identifier}></Input>
                </Form.Field>
                <Form.Field>
                    <label>新密码</label>
                    <Input type="password" {...password}></Input>
                </Form.Field>
                <Form.Button color="green" onClick={doReset}> 提交</Form.Button>
            </Form>
        </Segment>
    </div>;
};

export default EmailResetPasswordView;