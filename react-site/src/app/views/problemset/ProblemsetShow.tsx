import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Button, Dimmer, Grid, Header, Loader, Segment, Table } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { Markdown } from "../../common/Markdown";
import { useDocumentTitle } from "../../common/Utils";
import { showConfirm, showSuccessModal } from "../../dialogs/Dialog";
import JudgeStatusLabel from "../utils/JudgeStatusLabel";
import UserLink from "../utils/UserLink";
import problemsetClient from "./client/ProblemsetClient";
import { ProblemsetPublicInfo } from "./client/types";

const ProblemsetShow: React.FC<{}> = () => {
    const { id } = useParams<{ id: string }>();
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<ProblemsetPublicInfo | null>(null);
    useDocumentTitle(`${data?.name || "加载中..."} - 习题集`);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    const resp = await problemsetClient.getProblemsetFrontendInfo(parseInt(id));
                    setData(resp);
                    setLoaded(true);
                } catch { } finally { }
            })();
        }
    }, [id, loaded]);
    const remove = () => {
        showConfirm("您确认要删除此习题集吗?", async () => {
            try {
                await problemsetClient.removeProblemset(data!.id);
                window.location.href = "/problemset/list/1";
            } catch { } finally { }
        });
    };
    return <div>
        <Header as="h1">
            {data?.name || ""}
        </Header>
        {!loaded && <Segment>
            <div style={{ height: "400px" }}>
                <Dimmer active>
                    <Loader></Loader>
                </Dimmer>
            </div></Segment>}
        {loaded && data !== null && <Grid columns="2">
            <Grid.Column width="11">
                {data.description !== "" && <div>
                    <Header as="h3">
                        简介
                    </Header>
                    <Segment stacked>
                        <Markdown markdown={data.description}></Markdown>
                    </Segment>
                </div>}
                {data.problems.length !== 0 && <>
                    <Header as="h3">
                        题目列表
                    </Header>
                    <Segment stacked>
                        <Table>
                            <Table.Header>
                                <Table.Row>
                                    <Table.HeaderCell>题目</Table.HeaderCell>
                                    <Table.HeaderCell>我的提交</Table.HeaderCell>
                                </Table.Row>
                            </Table.Header>
                            <Table.Body>
                                {data.problems.map((x, i) => <Table.Row key={i}>
                                    <Table.Cell>
                                        <a target="_blank" rel="noreferrer" href={`/show_problem/${x.id}`}>{x.id} - {x.title}</a>
                                    </Table.Cell>
                                    <Table.Cell>
                                        <a target="_blank" rel="noreferrer" href={x.userResult.submissionID === -1 ? undefined : `/show_submission/${x.userResult.submissionID}`}>
                                            <JudgeStatusLabel status={x.userResult.status}></JudgeStatusLabel>
                                        </a>
                                    </Table.Cell>
                                </Table.Row>)}
                            </Table.Body>
                        </Table>
                    </Segment></>}
                {data.foreignProblems.length !== 0 && <>
                    <Header as="h3">
                        外部题目
                    </Header>
                    <Segment stacked>
                        <Table celled>
                            <Table.Header>
                                <Table.Row>
                                    <Table.HeaderCell>名称</Table.HeaderCell>
                                    <Table.HeaderCell>链接</Table.HeaderCell>
                                </Table.Row>
                            </Table.Header>
                            <Table.Body>
                                {data.foreignProblems.map((x, i) => <Table.Row key={i}>
                                    <Table.Cell>{x.name}</Table.Cell>
                                    <Table.Cell>
                                        <a href={x.url}>{x.url}</a>
                                    </Table.Cell>
                                </Table.Row>)}
                            </Table.Body>
                        </Table>
                    </Segment>
                </>}
            </Grid.Column>
            <Grid.Column width="5">
                <Segment stacked>
                    <Table basic="very">
                        <Table.Body>
                            <Table.Row>
                                <Table.Cell>习题集ID</Table.Cell>
                                <Table.Cell>{data.id}</Table.Cell>
                            </Table.Row>
                            <Table.Row>
                                <Table.Cell>创建时间</Table.Cell>
                                <Table.Cell>{data.createTime}</Table.Cell>
                            </Table.Row>
                            <Table.Row>
                                <Table.Cell>所有者</Table.Cell>
                                <Table.Cell><UserLink data={data.owner}></UserLink></Table.Cell>
                            </Table.Row>
                            <Table.Row>
                                <Table.Cell>权限</Table.Cell>
                                <Table.Cell>{data.private ? "私有" : "公开"}</Table.Cell>
                            </Table.Row>
                        </Table.Body>
                    </Table>
                    <Button color="green" onClick={() => showSuccessModal("解锁成功")}>
                        解锁权限
                    </Button>
                    {data.managable && <>
                        <Button color="green" as={Link} to={`${PUBLIC_URL}/problemset/edit/${data.id}`}>编辑</Button>
                        <Button color="red" onClick={remove}>删除</Button>
                    </>}
                </Segment>
            </Grid.Column>
        </Grid>}
    </div>;
};

export default ProblemsetShow;