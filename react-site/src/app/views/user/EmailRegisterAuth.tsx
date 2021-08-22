/**
 * 邮箱注册验证邮箱
 * 
 * 
 * */
import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { Dimmer, Form, Header, Input, Loader, Segment } from "semantic-ui-react";
import { useDocumentTitle, useInputValue } from "../../common/Utils";
import { showSuccessPopup } from "../../dialogs/Utils";
import userClient from "./client/UserClient";

const EmailRegisterAuth: React.FC<{}> = () => {

    const params = useParams<{ token: string }>();
    const token = decodeURIComponent(decodeURIComponent(params.token));
    const username = useInputValue();
    const [loading, setLoading] = useState(false);
    const doReset = async () => {
        try {
            setLoading(true);
            await userClient.doEmailAuth(username.value, token);
            showSuccessPopup("认证成功，即将跳转");
            setTimeout(() => window.location.href = "/", 500);
        } catch {

        } finally {
            setLoading(false);
        }
    }
    useDocumentTitle("验证邮箱");
    return <div style={{ maxWidth: "500px" }}>
        <Header as="h1">
            验证邮箱
        </Header>
        <Segment stacked>
            {loading && <Dimmer active>
                <Loader></Loader>
            </Dimmer>}
            <Form>
                <Form.Field>
                    <label>用户名(非邮箱)</label>
                    <Input {...username}></Input>
                </Form.Field>
                <Form.Button color="green" onClick={doReset}> 提交</Form.Button>
            </Form>
        </Segment>
    </div>;
};

export default EmailRegisterAuth;