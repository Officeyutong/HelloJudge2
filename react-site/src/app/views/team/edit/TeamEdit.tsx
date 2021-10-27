import { Schema, validate } from "jsonschema";
import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { Button, Checkbox, Dimmer, Divider, Form, Header, Input, Loader, Message, Segment } from "semantic-ui-react";
import { ButtonClickEvent } from "../../../common/types";
import { useDocumentTitle } from "../../../common/Utils";
import teamClient from "../client/TeamClient";
import { TeamRawData } from "../client/types";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-markdown";
// import "ace-builds/src-noconflict/mode-javascript";
import { useAceTheme } from "../../../states/StateUtils";
import { v4 as uuidv4 } from "uuid";
import { showErrorModal, showSuccessModal } from "../../../dialogs/Dialog";
import { Link } from "react-router-dom";
import { PUBLIC_URL } from "../../../App";
const allNumbersSchema: Schema = {
    type: "array",
    items: {
        type: "number"
    }
};
function validStuffThings(text: string): boolean {
    try {
        const data = JSON.parse(text);
        if (!validate(data, allNumbersSchema).valid) return false;
    } catch {
        return false;
    }
    return true;
}
const TeamEdit: React.FC<{}> = () => {
    const { team } = useParams<{ team: string }>();
    const teamID = parseInt(team);
    const [loaded, setLoaded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<null | TeamRawData>(null);
    const aceTheme = useAceTheme();
    const [teamStuff, setTeamStuff] = useState<{ problems: string; contests: string; problemsets: string }>({ contests: "", problems: "", problemsets: "" });
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setLoading(true);
                    const resp = await teamClient.getTeamRawData(teamID);
                    setTeamStuff({
                        problems: JSON.stringify(resp.team_problems),
                        contests: JSON.stringify(resp.team_contests),
                        problemsets: JSON.stringify(resp.team_problemsets)
                    });
                    setData(resp);
                    setLoaded(true);
                } catch { } finally {
                    setLoading(false);
                }
            })();
        }
    }, [loaded, teamID]);
    useDocumentTitle(`${data?.name || "加载中..."} - 团队编辑`);
    const update = async (evt: ButtonClickEvent) => {
        if (data === null) return;
        if (!validStuffThings(teamStuff.contests)) {
            showErrorModal("请填写格式正确的团队比赛");
            return;
        }
        if (!validStuffThings(teamStuff.problems)) {
            showErrorModal("请填写格式正确的团队题目");
            return;
        }
        if (!validStuffThings(teamStuff.problemsets)) {
            showErrorModal("请填写格式正确的团队习题集");
            return;
        }
        const target = evt.currentTarget;
        target.classList.add("loading");
        try {
            await teamClient.updateTeamInfo(data.id, {
                description: data.description,
                invite_code: data.invite_code,
                name: data.name,
                private: data.private,
                tasks: data.tasks,
                team_contests: JSON.parse(teamStuff.contests),
                team_problems: JSON.parse(teamStuff.problems),
                team_problemsets: JSON.parse(teamStuff.problemsets),
            });
            showSuccessModal("更新完成!");
        } catch { } finally {
            target.classList.remove("loading");
        }

    };
    return <>
        {!loaded && loading && <>
            <Segment stacked>
                <Dimmer active>
                    <Loader></Loader>
                </Dimmer>
                <div style={{ height: "400px" }}></div>
            </Segment>
        </>}
        {loaded && data !== null && <>
            <Header as="h1">
                {data.name}
            </Header>
            <Segment stacked>
                <Form>
                    <Form.Field>
                        <label>团队ID</label>
                        <p>{data.id}</p>
                    </Form.Field>
                    <Form.Field>
                        <label>团队名</label>
                        <Input value={data.name} onChange={(_, d) => setData({ ...data, name: d.value })}></Input>
                    </Form.Field>
                    <Form.Field>
                        <label>团队简介</label>
                        <AceEditor
                            value={data.description}
                            onChange={d => setData({ ...data, description: d })}
                            theme={aceTheme}
                            mode="markdown"
                            wrapEnabled
                            width="100%"
                            height="200px"
                        ></AceEditor>
                    </Form.Field>
                    <Form.Field>
                        <label>团队题目</label>
                        <AceEditor
                            value={teamStuff.problems}
                            onChange={d => setTeamStuff({ ...teamStuff, problems: d })}
                            theme={aceTheme}
                            // mode="javascript"
                            wrapEnabled
                            width="100%"
                            height="50px"
                        ></AceEditor>
                    </Form.Field>
                    <Form.Field>
                        <label>团队比赛</label>
                        <AceEditor
                            value={teamStuff.contests}
                            onChange={d => setTeamStuff({ ...teamStuff, contests: d })}
                            theme={aceTheme}
                            // mode="javascript"
                            wrapEnabled
                            width="100%"
                            height="50px"
                        ></AceEditor>
                    </Form.Field>
                    <Form.Field>
                        <label>团队习题集</label>
                        <AceEditor
                            value={teamStuff.problemsets}
                            onChange={d => setTeamStuff({ ...teamStuff, problemsets: d })}
                            theme={aceTheme}
                            // mode="javascript"
                            wrapEnabled
                            width="100%"
                            height="50px"
                        ></AceEditor>
                    </Form.Field>
                    <Message info>
                        <Message.Header>提示</Message.Header>
                        <Message.Content>
                            <p>团队题目、团队比赛、团队习题集的填写格式为：中括号内，用逗号分开的相应ID</p>
                            <p>团队内的用户会自动获得相应的使用权限。如果某个题目、比赛或者习题集被从团队内删除，则相应用户自动失去权限。</p>
                        </Message.Content>
                    </Message>
                    <Divider></Divider>
                    <Form.Field>
                        <Checkbox
                            checked={data.private}
                            toggle
                            onChange={() => setData({ ...data, private: !data.private })}
                            label="私有团队"
                        ></Checkbox>
                    </Form.Field>
                    {data.private && <Form.Field>
                        <label>邀请码</label>
                        <Input actionPosition="left" action={{
                            content: "随机生成",
                            onClick: () => setData({ ...data, invite_code: uuidv4() })
                        }} value={data.invite_code} onChange={(e, d) => setData({ ...data, invite_code: d.value })}></Input>
                    </Form.Field>}
                    <Button color="green" onClick={update}>
                        提交
                    </Button>
                    <Button color="red" as={Link} to={`${PUBLIC_URL}/team/${data.id}`}>
                        返回
                    </Button>
                </Form>
            </Segment>
        </>}
    </>;
};

export default TeamEdit;