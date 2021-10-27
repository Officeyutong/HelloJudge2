/**
 * 
 * 通用登录（用户名或邮箱登录）
 */

import md5 from "md5";
import { useState } from "react";
import { useSelector } from "react-redux";
import { Button, Container, Dimmer, Form, Grid, Header, Input, Loader, Segment } from "semantic-ui-react";
import { useDocumentTitle } from "../../common/Utils";
import { showErrorModal, showSuccessModal } from "../../dialogs/Dialog";
import { StateType } from "../../states/Manager";
import userClient from "./client/UserClient";

const LoginView: React.FC<{}> = () => {
    useDocumentTitle("用户登录");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const phoneAuth = useSelector((s: StateType) => s.userState.userData.usePhoneAuth);
    const salt = useSelector((s: StateType) => s.userState.userData.salt);
    const doLogin = async () => {
        if (username === "" || password === "") {
            showErrorModal("请输入用户名或密码!");
            return;
        }
        try {
            setLoading(true);
            await userClient.doLogin(username, md5(password + salt));
            window.location.href = ("/");
        } catch (e) { setLoading(false); } finally { }
    }
    const doResetPassword = async () => {
        if (phoneAuth) {
            window.location.href = ("/phone/reset_password");
        } else {
            try {
                if (username === "") {
                    showErrorModal("请输入用户名");
                    return;
                }
                setLoading(true);
                await userClient.doRequireResetPassword(username);
                showSuccessModal("发送成功，请前往邮箱查收.");
            } catch (e) {

            } finally {
                setLoading(false);
            }
        }
    };
    return <div>
        <Header as="h1">
            登录
        </Header>
        <Segment stacked style={{ maxWidth: "60%" }}>
            {loading && <Dimmer active>
                <Loader>加载中</Loader></Dimmer>}
            <Form>
                <Form.Field>
                    <label>用户名或邮箱</label>
                    <Input value={username} onChange={(_, d) => setUsername(d.value)}></Input>
                </Form.Field>
                <Form.Field>
                    <label>密码</label>
                    <Input value={password} onChange={(_, d) => setPassword(d.value)} type="password"></Input>
                </Form.Field>
                <Grid columns="2">
                    <Grid.Column>
                        <Button size="small" color="green" onClick={doLogin}>
                            登录
                        </Button>
                        <Button size="small" color="blue" onClick={() => {
                            if (phoneAuth) { window.location.href = ("/phone/register"); } else { window.location.href = ("/register") }
                        }}>注册</Button>
                    </Grid.Column>
                    <Grid.Column>
                        <Container textAlign="right">
                            <Button.Group size="small">
                                <Button color="blue" size="tiny" onClick={doResetPassword}>重置密码</Button>

                                <Button color="red" size="tiny" as="a" href="/user/forget_username">
                                    忘记用户名
                                </Button>
                            </Button.Group>
                        </Container>
                    </Grid.Column>
                </Grid>
            </Form>
        </Segment>
    </div>;
};

export default LoginView;