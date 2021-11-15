import React, { useEffect, useState } from "react";
import { useHistory, useParams } from "react-router";
import { Button, Dimmer, Form, Header, Input, Loader, Message, Segment } from "semantic-ui-react";
import { useDocumentTitle } from "../../common/Utils";
import challengeClient from "./client/ChallengeClient";
import { ChallengeRawData } from "./client/types";
import AceEditor from "react-ace";
import { useAceTheme } from "../../states/StateUtils";
import { ButtonClickEvent } from "../../common/types";
import { showConfirm, showErrorModal, showSuccessModal } from "../../dialogs/Dialog";
import { PUBLIC_URL } from "../../App";
import { Schema, validate } from "jsonschema";
const ChallengeEdit: React.FC<{}> = () => {
    const { id } = useParams<{ id: string }>();
    const numberID = parseInt(id);
    const [loading, setLoading] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<null | ChallengeRawData>(null);
    const theme = useAceTheme();
    const [problemsetListCache, setProblemsetListCache] = useState("");
    const history = useHistory();
    useEffect(() => {
        if (!loaded) {
            setLoading(true);
            challengeClient.getChallengeRawData(numberID).then(resp => {
                setData(resp);
                setProblemsetListCache(JSON.stringify(resp.problemsetList));
                setLoaded(true);
                setLoading(false);
            });
        }
    }, [loaded, numberID]);
    useDocumentTitle(`${data?.name || "加载中..."} - 编辑挑战`);
    const submit = async (evt: ButtonClickEvent) => {
        if (data === null) return;
        try {
            JSON.parse(problemsetListCache)
        } catch {
            showErrorModal("请在习题集列表处输入合法的JSON!");
            return;
        }
        const parsed = JSON.parse(problemsetListCache);
        if (!validate(parsed, {
            type: "array", items: {
                type: "number"
            }
        } as Schema).valid) {
            showErrorModal("请在习题集列表处输入一个元素只包含整数的JSON！");
            return;
        }
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            await challengeClient.updateChallenge(
                data.id,
                data.name,
                data.level,
                data.description,
                JSON.parse(problemsetListCache)
            );
            showSuccessModal("保存完成!");
        } catch { } finally {
            target.classList.remove("loading");
        }
    };
    const remove = (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        showConfirm("您确认要删除此挑战吗？此操作不可逆。", async () => {
            try {
                target.classList.add("loading");
                await challengeClient.removeChallenge(data!.id);
                history.push(`${PUBLIC_URL}/challenge/list`);
            } catch { } finally {
            }
        });
    };
    return <>
        {loading && <Segment stacked>
            <div style={{ height: "400px" }}></div>
            <Dimmer active>
                <Loader>加载中</Loader>
            </Dimmer>
        </Segment>}
        {loaded && data !== null && <>
            <Header as="h1">
                编辑挑战 - {data.name}
            </Header>
            <Segment stacked>
                <Form>
                    <Form.Field>
                        <label>挑战名</label>
                        <Input value={data.name} onChange={(_, d) => setData({ ...data, name: d.value })}></Input>
                    </Form.Field>
                    <Form.Field>
                        <label>挑战描述</label>
                        <AceEditor
                            wrapEnabled
                            value={data.description}
                            onChange={v => setData({ ...data, description: v })}
                            width="100%"
                            height="200px"
                            theme={theme}
                        >
                        </AceEditor>
                    </Form.Field>
                    <Form.Field>
                        <label>挑战等级</label>
                        <Input value={data.level} type="number" onChange={(_, d) => setData({ ...data, level: parseInt(d.value) })}></Input>
                    </Form.Field>
                    <Form.Field>
                        <label>习题集列表</label>
                        <AceEditor
                            wrapEnabled
                            value={problemsetListCache}
                            onChange={setProblemsetListCache}
                            width="100%"
                            height="100px"
                            theme={theme}
                        >
                        </AceEditor>
                    </Form.Field>
                    <Message info>
                        <Message.Header>关于习题集列表</Message.Header>
                        <Message.Content>
                            <p>中括号内，使用英文逗号分隔开习题集ID。</p>
                        </Message.Content>
                    </Message>
                    <Message info>
                        <Message.Header>关于挑战等级</Message.Header>
                        <Message.Content>
                            <p>每个挑战的等级必须为一个互不相同正整数</p>
                            <p>用户如果要获得使用一个挑战(非level=1)的资格，则必须通过比该挑战level低的所有挑战</p>
                            <p>level=1的挑战不需要前置条件</p>
                            <p>请根据以上两条合理安排挑战等级。</p>
                            <p>通过一个挑战需要获取challenge.finish.挑战ID.习题集ID1 challenge.finish.挑战ID.习题集ID2...等该挑战下的所有习题集</p>
                            <p> 通过一个挑战后申请获取challenge.finish.挑战ID.all权限</p>
                            <p>需要具有challenge.access.挑战ID(level=1的挑战除外)才可访问一个挑战</p>
                        </Message.Content>
                    </Message>
                    <Button color="green" onClick={submit}>
                        保存
                    </Button>
                    <Button color="red" onClick={remove}>
                        删除
                    </Button>
                </Form>
            </Segment>
        </>}
    </>;
};

export default ChallengeEdit;