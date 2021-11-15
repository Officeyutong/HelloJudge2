import React, { useState } from "react";
import { useHistory } from "react-router";
import { Button, Dimmer, Form, Header, Input, Loader, Modal, Segment } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { useDocumentTitle, useInputValue } from "../../common/Utils";
import SendSMSCodeDialog from "../utils/SendSMSCode";
import userClient from "./client/UserClient";

const PhoneAuth: React.FC<{}> = () => {
    useDocumentTitle("绑定手机号");
    const [loading, setLoading] = useState(false);
    const history = useHistory();
    const phone = useInputValue();
    const code = useInputValue();
    const [showDialog, setShowDialog] = useState(false);
    const submit = async () => {
        try {
            setLoading(true);
            await userClient.doPhoneAuth(code.value, phone.value);
            history.push(`${PUBLIC_URL}/`);
        } catch { } finally {
            setLoading(false);
        }
    };
    const [codeSended, setCodeSended] = useState(false);
    return <>
        <Header as="h1">
            绑定手机号
        </Header>
        <Segment stacked style={{ maxWidth: "35%" }}>
            {loading && <Dimmer active>
                <Loader></Loader>
            </Dimmer>}
            <Form>
                <Form.Field>
                    <label>手机号码</label>
                    <Input {...phone}></Input>
                </Form.Field>
                <Form.Field>
                    <label>验证码</label>
                    <Input {...code}></Input>
                </Form.Field>
                <Button color="green" onClick={() => setShowDialog(true)}>
                    发送验证码
                </Button>
                {codeSended && <Button color="green" onClick={submit}>
                    提交
                </Button>}
            </Form>
        </Segment>
        {showDialog && <Modal open={showDialog} closeOnDimmerClick={false}>
            <SendSMSCodeDialog
                mustNotUse={true}
                phone={phone.value}
                onClose={() => {
                    setShowDialog(false);
                    setCodeSended(true);
                }}
            ></SendSMSCodeDialog>
        </Modal>}
    </>;
};

export default PhoneAuth;