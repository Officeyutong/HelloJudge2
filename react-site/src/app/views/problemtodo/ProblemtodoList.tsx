import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Button, Dimmer, Header, Loader, Segment, Table } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { ButtonClickEvent } from "../../common/types";
import { useDocumentTitle } from "../../common/Utils";
import { showSuccessPopup } from "../../dialogs/Utils";
import JudgeStatusLabel from "../utils/JudgeStatusLabel";
import problemtodoClient from "./client/ProblemtodoClient";
import { ProblemtodoEntry } from "./client/types";
const ProblemtodoList: React.FC<{}> = () => {
    const [loaded, setLoaded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<ProblemtodoEntry[]>([]);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setLoading(true);
                    const resp = await problemtodoClient.getAll();
                    setData(resp);
                    setLoading(false);
                    setLoaded(true);
                } catch { } finally {
                }
            })();
        }
    }, [loaded]);
    useDocumentTitle("待做题目列表");
    const remove = async (id: number, evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            await problemtodoClient.remove(id);
            showSuccessPopup("删除成功!");
            setData(d => d.filter(q => q.id !== id));
        } catch { } finally {
            target.classList.remove("loading");
        }
    };
    return <>
        <Header as="h1">
            待做题目列表
        </Header>
        {!loaded && loading && <div style={{ height: "400px" }}>
            <Dimmer active>
                <Loader></Loader>
            </Dimmer>
        </div>}
        {loaded && <>
            <Segment stacked>
                <Table textAlign="center">
                    <Table.Header>
                        <Table.Row>
                            <Table.HeaderCell>题目</Table.HeaderCell>
                            <Table.HeaderCell>加入时间</Table.HeaderCell>
                            <Table.HeaderCell>提交状态</Table.HeaderCell>
                            <Table.HeaderCell>操作</Table.HeaderCell>
                        </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {data.map((x, i) => <Table.Row key={i}>
                            <Table.Cell>
                                <Link to={`${PUBLIC_URL}/show_problem/${x.id}`}>#{x.id}. {x.title}</Link>
                            </Table.Cell>
                            <Table.Cell>{x.joinTime}</Table.Cell>
                            <Table.Cell>
                                {(() => {
                                    const inner = <JudgeStatusLabel status={x.submission.status}></JudgeStatusLabel>;
                                    if (x.submission.id === -1) return inner;
                                    return <Link to={`${PUBLIC_URL}/show_submission/${x.id}`}>{inner}</Link>
                                })()}
                            </Table.Cell>
                            <Table.Cell>
                                <Button size="small" onClick={evt => remove(x.id, evt)} color="red">
                                    删除
                                </Button>
                            </Table.Cell>
                        </Table.Row>)}
                    </Table.Body>
                </Table>
            </Segment>
        </>}
    </>;
};

export default ProblemtodoList;