import _ from "lodash";
import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Button, Checkbox, Dimmer, Divider, Form, Header, Icon, Input, Loader, Segment, Table, TextArea } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { ButtonClickEvent } from "../../common/types";
import { useDocumentTitle } from "../../common/Utils";
import { showSuccessModal } from "../../dialogs/Dialog";
import UserLink from "../utils/UserLink";
import BatchAddDialog from "./BatchAddDialog";
import problemsetClient from "./client/ProblemsetClient";
import { ProblemsetEditInfo } from "./client/types";
(window as typeof window & { lodash: any }).lodash = _;
const ProblemsetEdit: React.FC<{}> = () => {
    const { id } = useParams<{ id: string }>();
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<ProblemsetEditInfo | null>(null);
    const [showBatchAdd, setShowBatchAdd] = useState(false);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    const resp = await problemsetClient.getProblemsetEditInfo(parseInt(id));
                    setData(resp);
                    setLoaded(true);
                } catch { } finally { }
            })();
        }
    }, [loaded, id]);
    useDocumentTitle(`${data?.name || "加载中..."} - 编辑习题集`);
    const save = async (evt: ButtonClickEvent) => {
        if (data === null) return;
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            await problemsetClient.updateProblemset({
                description: data.description,
                foreignProblems: data.foreignProblems,
                id: data.id,
                invitationCode: data.invitationCode,
                name: data.name,
                private: data.private,
                problems: data.problems,
                showRanklist: data.showRanklist
            });
            showSuccessModal("保存完成");
        } catch { } finally {
            target.classList.remove("loading");
        }
    };
    return <div>
        {!loaded && <Segment>
            <div style={{ height: "400px" }}>
                <Dimmer active>
                    <Loader></Loader>
                </Dimmer>
            </div>
        </Segment>}
        {loaded && data !== null && <>
            <Header as="h1">
                {data.name}
            </Header>
            <Segment stacked>
                <Form>
                    <Form.Field>
                        <label>创建者</label>
                        <UserLink data={data.owner}></UserLink>
                    </Form.Field>
                    <Form.Field>
                        <label>名称</label>
                        <Input fluid value={data.name} onChange={(_, d) => setData({ ...data, name: d.value })}></Input>
                    </Form.Field>
                    <Form.Field>
                        <Checkbox toggle checked={data.private === 1} onClick={() => setData({ ...data, private: 1 - data.private as 0 | 1 })} label="私有"></Checkbox>
                    </Form.Field>
                    <Form.Field>
                        <label>邀请码</label>
                        <Input value={data.invitationCode} onChange={(_, d) => setData({ ...data, invitationCode: d.value })} disabled={!data.private}></Input>
                    </Form.Field>
                    <Divider></Divider>
                    <Form.Field>
                        <label>说明</label>
                        <TextArea value={data.description} onChange={(_, d) => setData({ ...data, description: d.value as string })}></TextArea>
                    </Form.Field>
                    <Form.Field>
                        <label>题目列表</label>
                        <Table >
                            <Table.Header>
                                <Table.Row>
                                    <Table.HeaderCell>题目ID</Table.HeaderCell>
                                    <Table.HeaderCell>操作</Table.HeaderCell>
                                </Table.Row>
                            </Table.Header>
                            <Table.Body>
                                {data.problems.map((x, i) => <Table.Row key={i}>
                                    <Table.Cell>
                                        <Input type="number" value={x} onChange={(e, d) => setData({ ...data, problems: _(data.problems).set(i, parseInt(d.value)).value() })}></Input>
                                    </Table.Cell>
                                    <Table.Cell>
                                        <Button.Group>
                                            <Button onClick={() => {
                                                const arr = [...data.problems];
                                                [arr[i], arr[i - 1]] = [arr[i - 1], arr[i]];
                                                setData({ ...data, problems: arr });
                                            }} icon color="blue" disabled={i === 0}>
                                                <Icon name="angle up"></Icon>
                                            </Button>
                                            <Button onClick={() => {
                                                const arr = [...data.problems];
                                                [arr[i], arr[i + 1]] = [arr[i + 1], arr[i]];
                                                setData({ ...data, problems: arr });
                                            }} icon color="blue" disabled={i === data.problems.length - 1}>
                                                <Icon name="angle down"></Icon>
                                            </Button>
                                            <Button icon color="green" onClick={() => {
                                                setData({ ...data, problems: data.problems.filter((_, j) => j !== i) })
                                            }} >
                                                <Icon name="times"></Icon>
                                            </Button>
                                        </Button.Group>
                                    </Table.Cell>
                                </Table.Row>)}
                                <Table.Row>
                                    <Table.Cell>
                                        <Button color="green" onClick={() => setData({ ...data, problems: [...data.problems, (parseInt(`${_.last(data.problems)}`) || 0) + 1] })}>
                                            添加
                                        </Button>
                                    </Table.Cell>
                                </Table.Row>
                            </Table.Body>
                        </Table>
                    </Form.Field>
                    <Form.Field>
                        <label>外部题目</label>
                        <Table>
                            <Table.Header>
                                <Table.Row>
                                    <Table.HeaderCell>名称</Table.HeaderCell>
                                    <Table.HeaderCell>链接</Table.HeaderCell>
                                    <Table.HeaderCell>操作</Table.HeaderCell>
                                </Table.Row>
                            </Table.Header>
                            <Table.Body>
                                {data.foreignProblems.map((x, i) => <Table.Row>
                                    <Table.Cell>
                                        <Input value={x.name} onChange={(e, d) => setData({ ...data, foreignProblems: _.set(data.foreignProblems, i, { name: d.value, url: x.url }) })}></Input>
                                    </Table.Cell>
                                    <Table.Cell>
                                        <Input value={x.url} onChange={(e, d) => setData({ ...data, foreignProblems: _.set(data.foreignProblems, i, { url: d.value, name: x.name }) })}></Input>
                                    </Table.Cell>
                                    <Table.Cell>
                                        <Button.Group>
                                            <Button onClick={() => {
                                                const arr = [...data.foreignProblems];
                                                [arr[i], arr[i - 1]] = [arr[i - 1], arr[i]];
                                                setData({ ...data, foreignProblems: arr });
                                            }} icon color="blue" disabled={i === 0}>
                                                <Icon name="angle up"></Icon>
                                            </Button>
                                            <Button onClick={() => {
                                                const arr = [...data.foreignProblems];
                                                [arr[i], arr[i + 1]] = [arr[i + 1], arr[i]];
                                                setData({ ...data, foreignProblems: arr });
                                            }} icon color="blue" disabled={i === data.foreignProblems.length - 1}>
                                                <Icon name="angle down"></Icon>
                                            </Button>
                                            <Button icon color="green" onClick={() => {
                                                setData({ ...data, foreignProblems: data.foreignProblems.filter((_, j) => j !== i) })
                                            }} >
                                                <Icon name="times"></Icon>
                                            </Button>
                                        </Button.Group>
                                    </Table.Cell>
                                </Table.Row>)}
                                <Table.Row>
                                    <Table.Cell>
                                        <Button color="green" onClick={() => setData({ ...data, foreignProblems: [...data.foreignProblems, { name: "题目名称", url: "题目链接" }] })}>
                                            添加
                                        </Button>
                                        <Button color="green" onClick={() => setShowBatchAdd(true)}>
                                            批量添加
                                        </Button>

                                    </Table.Cell>
                                </Table.Row>
                            </Table.Body>
                        </Table>
                    </Form.Field>
                    <Button color="green" onClick={save}>保存</Button>
                    <Button color="green" as={Link} to={`${PUBLIC_URL}/problemset/show/${data.id}`}>返回</Button>
                </Form>
            </Segment>
        </>}
        {showBatchAdd && <BatchAddDialog open={showBatchAdd} onClose={() => setShowBatchAdd(false)} finish={resp => {
            setData({
                ...data!, foreignProblems: [...data!.foreignProblems, ...resp]
            })
        }}></BatchAddDialog>}
    </div>;
};

export default ProblemsetEdit;