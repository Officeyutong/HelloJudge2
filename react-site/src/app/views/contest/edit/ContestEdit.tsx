import React, { useEffect, useState } from "react";
import { useParams } from "react-router";
import { Button, Checkbox, Dimmer, Divider, Form, Header, Input, Loader, Segment } from "semantic-ui-react";
import { useDocumentTitle } from "../../../common/Utils";
import contestClient from "../client/ContestClient";
import { ContestEditRawDataResponse } from "../client/types";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-markdown";
import { useAceTheme } from "../../../states/StateUtils";
import DateTimePickler from "react-datetime";
import "react-datetime/css/react-datetime.css";
import { DateTime } from "luxon";
import 'moment/locale/zh-cn';
import ProblemEditArea from "./ProblemEditArea";
import * as uuid from "uuid";
import { ButtonClickEvent } from "../../../common/types";
import { Link } from "react-router-dom";
import { PUBLIC_URL } from "../../../App";
import { showSuccessModal } from "../../../dialogs/Dialog";
const ContestEdit: React.FC<{}> = () => {
    const { id } = useParams<{ id: string }>();
    const numberID = parseInt(id);
    const [data, setData] = useState<ContestEditRawDataResponse | null>(null);
    const [loaded, setLoaded] = useState(false);
    const theme = useAceTheme();
    useDocumentTitle(`${data?.name || "加载中..."} - 编辑比赛`);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    const resp = await contestClient.getContestRawData(numberID);
                    setData(resp);
                    setLoaded(true);
                } catch { } finally { }
            })();
        }
    }, [loaded, numberID]);
    const save = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        if (data === null) return;
        try {
            target.classList.add("loading");
            await contestClient.updateContest(numberID, {
                description: data.description,
                end_time: data.end_time,
                invite_code: data.invite_code,
                judge_result_visible: data.judge_result_visible,
                name: data.name,
                private_contest: data.private_contest,
                problems: data.problems,
                rank_criterion: data.rank_criterion,
                ranklist_visible: data.ranklist_visible,
                start_time: data.start_time
            });
            showSuccessModal("保存完成");
        } catch { } finally {
            target.classList.remove("loading");
        }
    }
    return <>
        {!loaded && <div style={{ height: "400px" }}>
            <Dimmer active>
                <Loader></Loader>
            </Dimmer>
        </div>}
        {loaded && data !== null && <>
            <Header as="h1">
                {data.name} - 编辑
            </Header>
            <Segment stacked>
                <Form as="div">
                    <Form.Input
                        label="比赛名"
                        value={data.name}
                        onChange={(_, d) => setData(data => ({ ...data!, name: d.value }))}
                        disabled={data.closed}
                    ></Form.Input>
                    <Form.Field>
                        <label>比赛描述</label>
                        <AceEditor
                            value={data.description}
                            onChange={v => setData(data => ({ ...data!, description: v }))}
                            theme={theme}
                            mode="markdown"
                            height="150px"
                            width="100%"
                        ></AceEditor>
                    </Form.Field>
                    <Form.Field disabled={data.closed}>
                        <label>开始时间</label>
                        <DateTimePickler
                            value={DateTime.fromSeconds(data.start_time).toJSDate()}
                            onChange={v => {
                                if (typeof v === "string") return;
                                setData(data => ({ ...data!, start_time: Math.floor(DateTime.fromSeconds(v.unix()).set({ second: 0 }).toSeconds()) }));
                            }}
                            locale="zh-cn"

                        ></DateTimePickler>
                    </Form.Field>
                    <Form.Field disabled={data.closed}>
                        <label>结束时间</label>
                        <DateTimePickler
                            value={DateTime.fromSeconds(data.end_time).toJSDate()}
                            onChange={v => {
                                if (typeof v === "string") return;
                                setData(data => ({ ...data!, end_time: Math.floor(DateTime.fromSeconds(v.unix()).set({ second: 0 }).toSeconds()) }));
                            }}
                            locale="zh-cn"
                        ></DateTimePickler>
                    </Form.Field>
                    <Divider></Divider>
                    <Form.Field disabled={data.closed}>
                        <label>题目列表</label>
                        <ProblemEditArea
                            data={data.problems}
                            update={d => setData(data => ({ ...data!, problems: d }))}
                        ></ProblemEditArea>
                    </Form.Field>
                    <Divider></Divider>
                    <Form.Field disabled={data.closed}>
                        <label>排名依据</label>
                        <Button.Group>
                            <Button
                                onClick={() => setData(data => ({ ...data!, rank_criterion: "max_score" }))}
                                active={data.rank_criterion === "max_score"}
                            >
                                题目最高得分
                            </Button>
                            <Button
                                onClick={() => setData(data => ({ ...data!, rank_criterion: "last_submit" }))}
                                active={data.rank_criterion === "last_submit"}
                            >
                                题目最后一次提交
                            </Button>
                            <Button
                                onClick={() => setData(data => ({ ...data!, rank_criterion: "penalty" }))}
                                active={data.rank_criterion === "penalty"}
                            >
                                罚时
                            </Button>
                        </Button.Group>
                    </Form.Field>
                    <Form.Checkbox disabled={data.closed} toggle label="比赛时显示排行总榜" checked={data.ranklist_visible} onChange={() => setData(data => ({ ...data!, ranklist_visible: !data!.ranklist_visible }))}></Form.Checkbox>
                    <Form.Checkbox disabled={data.closed} toggle label="比赛时可以得知评测结果" checked={data.judge_result_visible} onChange={() => setData(data => ({ ...data!, judge_result_visible: !data!.judge_result_visible }))}></Form.Checkbox>
                    <Divider></Divider>
                    <Form.Field>
                        <label>权限设定</label>
                        <Checkbox toggle label="私有比赛" checked={data.private_contest} onChange={() => setData(data => ({ ...data!, private_contest: !data!.private_contest }))}></Checkbox>

                    </Form.Field>
                    {data.private_contest && <Form.Field>
                        <label>邀请码</label>
                        <Input actionPosition="left" action={{
                            content: "随机生成",
                            onClick: () => setData(data => ({ ...data!, invite_code: uuid.v4() }))
                        }} value={data.invite_code} onChange={(e, d) => setData(data => ({ ...data!, invite_code: d.value }))}></Input>
                    </Form.Field>}
                    <Button color="green" onClick={save}>
                        提交
                    </Button>
                    <Button color="red" as={Link} to={`${PUBLIC_URL}/contest/${data.id}`}>
                        返回
                    </Button>
                </Form>
            </Segment>
        </>}

    </>;
};

export default ContestEdit;