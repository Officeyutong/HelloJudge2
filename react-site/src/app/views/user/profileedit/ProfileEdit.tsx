import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Button, Checkbox, Dimmer, Divider, Form, Grid, Header, Input, Loader, Segment } from "semantic-ui-react";
import { useCurrentUid, useDocumentTitle, useInputValue, usePasswordSalt } from "../../../common/Utils";
import { UserProfileResponse } from "../client/types";
import userClient from "../client/UserClient";
import AceEditor from "react-ace";
import { useAceTheme } from "../../../states/StateUtils";
import { v4 as uuidv4 } from "uuid";
import ShowAllPermissions from "./ShowAllPermissions";
import { showErrorModal, showSuccessModal } from "../../../dialogs/Dialog";
import md5 from "md5";
const ProfileEdit: React.FC<{}> = () => {
    const uid = parseInt(useParams<{ uid: string }>().uid);
    const [data, setData] = useState<UserProfileResponse | null>(null);
    const [loaded, setLoaded] = useState(false);
    const [loading, setLoading] = useState(false);
    const pwd1 = useInputValue();
    const pwd2 = useInputValue();
    const aceTheme = useAceTheme();
    const [showing, setShowing] = useState(false);
    const salt = usePasswordSalt();
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setLoading(true);
                    const resp = await userClient.getUserProfile(uid);
                    setData(resp);
                    setLoaded(true);
                } catch { } finally { setLoading(false); }
            })();
        }
    }, [loaded, uid]);
    useDocumentTitle(`${data?.username || "加载中..."} - 修改个人信息`);
    const baseUid = useCurrentUid();
    const submit = async () => {
        const changed = pwd1.value !== "";
        if (changed && pwd1.value !== pwd2.value) {
            showErrorModal("两次密码不相同！");
            return;
        }
        try {
            setLoading(true);
            await userClient.updateProfile(uid, {
                banned: data!.banned,
                changePassword: changed,
                description: data!.description,
                email: data!.email,
                newPassword: md5(pwd1.value + salt),
                permission_group: data!.permission_group,
                permissions: data!.permissions,
                username: data!.username
            });
            showSuccessModal("更新完成!");
        } catch { } finally {
            setLoading(false);
        }
    };
    const toggleAdminMode = async () => {
        try {
            setLoading(true);
            await userClient.toggleAdminMode();
            window.location.reload();
        } catch { } finally { }
    };
    return <div>
        <Header as="h1">
            用户资料编辑
        </Header>
        <Segment stacked>
            {loading && data === null && <div style={{ height: "400px" }}><Dimmer active><Loader></Loader></Dimmer></div>}
            {data !== null && <div>
                {loading && data !== null && <Dimmer active> <Loader></Loader></Dimmer>}
                <Form>
                    <Form.Field disabled>
                        <label>用户名</label>
                        <Input value={data.username} onChange={(_, d) => setData({ ...data, username: d.value })}></Input>
                    </Form.Field>
                    <Form.Field disabled>
                        <label>电子邮箱</label>
                        <Input value={data.email} onChange={(_, d) => setData({ ...data, email: d.value })}></Input>
                    </Form.Field>
                    <Form.Field>
                        <label>个人简介</label>
                        <AceEditor
                            value={data.description}
                            onChange={v => setData({ ...data, description: v })}
                            mode="markdown"
                            theme={aceTheme}
                            name={uuidv4()}
                            width="100%"
                            height="400px"
                        ></AceEditor>
                    </Form.Field>
                    <Form.Field>
                        <label>头像</label>
                        请前往<a href="https://en.gravatar.com/">https://en.gravatar.com/</a>进行更改.
                    </Form.Field>
                    <Form.Field>
                        <label>手机号验证</label>
                        {data.phone_verified ? <div>您的手机号码 {data.phone_number} 已经经过验证</div> : <div style={{ fontSize: "large" }}>请前往<a href="/phoneauth">此处</a>验证手机号</div>}
                    </Form.Field>
                    <Form.Field>
                        <label>权限包领取</label>
                        {data.phone_verified ? <div> <a href="/permissionpack/user_packs" target="_blank">请前往此处进行操作</a></div> : <div style={{ fontSize: "large" }}>请先验证手机号后再尝试领取权限包！</div>}
                    </Form.Field>
                    <Divider></Divider>
                    <Form.Field>
                        <label>更改密码(不需要请留空)</label>
                        <Form.Group widths="equal">
                            <Form.Field>
                                <label>密码</label>
                                <Input type="password" {...pwd1}></Input>
                            </Form.Field>
                            <Form.Field>
                                <label>重复密码</label>
                                <Input type="password" {...pwd2}></Input>
                            </Form.Field>
                        </Form.Group>
                    </Form.Field>
                    <Divider></Divider>
                    <Form.Field>
                        <label>权限组</label>
                        <Input value={data.permission_group} onChange={(_, d) => setData({ ...data, permission_group: d.value })}></Input>
                    </Form.Field>
                    <Form.Field>
                        <label>组权限列表</label>
                        <div>
                            <Grid columns="8">
                                {data.group_permissions.map((x, i) => <Grid.Column key={i}>
                                    <div style={{ wordBreak: "break-word" }}>{x}</div>
                                </Grid.Column>)}
                            </Grid>
                        </div>
                    </Form.Field>
                    <Form.Field>
                        <label>用户权限列表</label>
                        <AceEditor
                            value={data.permissions.join("\n")}
                            onChange={v => setData({ ...data, permissions: v.trim().split("\n") })}
                            mode="plain_text"
                            theme={aceTheme}
                            name={uuidv4()}
                            width="100%"
                            height="400px"
                        ></AceEditor>
                    </Form.Field>
                    <Button size="tiny" onClick={() => setShowing(true)} color="green">查看所有权限</Button>
                    {data.managable && <>
                        <Divider></Divider>
                        <Checkbox toggle label="账户封禁" checked={data.banned !== 0} onChange={(_, d) => setData({ ...data, banned: (d.checked ? 1 : 0) })}></Checkbox>
                    </>}
                    <Divider></Divider>
                    <Button color="green" onClick={submit}>提交</Button>
                    {data.canSetAdmin && baseUid === data.id && <Button color="green" onClick={toggleAdminMode}>
                        {data.permission_group === "admin" ? "关闭管理员模式" : "打开管理员模式"}
                    </Button>}
                </Form>
            </div>}
        </Segment>
        {showing && <ShowAllPermissions uid={uid} onClose={() => setShowing(false)}></ShowAllPermissions>}
    </div>;
};

export default ProfileEdit;