import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Button, Container, Dimmer, Divider, Grid, Header, Icon, Input, Loader, Modal, Pagination, Segment, Table } from "semantic-ui-react";
import { ButtonClickEvent } from "../../common/types";
import { useDocumentTitle } from "../../common/Utils";
import problemsetClient from "./client/ProblemsetClient";
import { ProblemsetListItem } from "./client/types";



const ProblemsetList: React.FC<{}> = () => {
    useDocumentTitle("习题集列表");

    const params = useParams<{ page: string }>();
    const [showModal, setShowModal] = useState(false);
    const [code, setCode] = useState("");
    const [currentID, setCurrentID] = useState(-1);
    const [data, setData] = useState<ProblemsetListItem[]>([]);
    const [loaded, setLoaded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [page, setPage] = useState(-1);
    const [pageCount, setPageCount] = useState(0);
    const createProblemset = async (evt: ButtonClickEvent) => {
        try {
            setLoading(true);
            const id = await problemsetClient.createProblemset();
            window.open(`/problemset/show/${id}`, "_blank");
        } catch { } finally {
            setLoading(false);
        }
    };
    const doUnlock = async () => {
        try {
            await problemsetClient.unlockProblemset(currentID, code);
            window.location.href = `/problemset/show/${currentID}`;
        } catch { } finally {

        }
    };
    const loadPage = async (page: number) => {
        try {
            setLoading(true);
            const data = await problemsetClient.getProblemSetList(page);
            setData(data.data);
            setPage(page);
            setPageCount(data.pageCount);
            setLoaded(true);
        } catch { } finally {
            setLoading(false);
        }
    };
    useEffect(() => {
        if (!loaded) {
            loadPage(parseInt(params.page || "1"));
        }
    }, [loaded, params.page]);
    return <div>
        <Header as="h1">
            习题集
        </Header>
        {!loaded && <Segment>
            <div style={{ height: "300px" }}>
                <Dimmer active>
                    <Loader></Loader>
                </Dimmer>
            </div>
        </Segment>}
        {loaded && <Segment stacked>
            {loading && <Dimmer active><Loader></Loader></Dimmer>}
            <Container textAlign="right">
                <Button as="div" color="green" onClick={createProblemset}>
                    创建
                </Button>
            </Container>
            <Divider></Divider>
            <Table basic="very">
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell textAlign="center">名称</Table.HeaderCell>
                        <Table.HeaderCell textAlign="center">权限</Table.HeaderCell>
                        <Table.HeaderCell textAlign="center">题目数量</Table.HeaderCell>
                        <Table.HeaderCell textAlign="center">创建者</Table.HeaderCell>
                        <Table.HeaderCell textAlign="center">创建时间</Table.HeaderCell>

                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {data.map((x, i) => <Table.Row key={i}>
                        <Table.Cell textAlign="center">
                            <a target="_blank" rel="noreferrer" style={{ cursor: 'pointer' }} onClick={(!(x.accessible || !x.private)) ? () => {
                                setCode("");
                                setCurrentID(x.id);
                                setShowModal(true);
                            } : undefined} href={(x.accessible || !x.private) ? `/problemset/show/${x.id}` : undefined}>#{x.id}. {x.name}</a>
                        </Table.Cell>
                        <Table.Cell textAlign="center"
                            positive={x.accessible || x.private === 0}
                            negative={(!x.accessible) && x.private === 1}
                        >
                            {x.private ? <div>
                                {x.accessible ? <Icon name="lock open"></Icon> : <Icon name="lock"></Icon>}
                            </div> : <div>公开</div>}
                        </Table.Cell>
                        <Table.Cell textAlign="center">
                            {x.problemCount !== -1 && <div>{x.problemCount}</div>}
                        </Table.Cell>
                        <Table.Cell textAlign="center">
                            <a href={`/profile/${x.owner.uid}`}>{x.owner.username}</a>
                        </Table.Cell>
                        <Table.Cell textAlign="center">
                            {x.createTime}
                        </Table.Cell>
                    </Table.Row>)}
                </Table.Body>
            </Table>
            <Grid columns="3" centered >
                <Grid.Column>
                    <Pagination
                        totalPages={pageCount}
                        activePage={page}
                        onPageChange={(e, d) => loadPage(d.activePage as number)}
                    ></Pagination>
                </Grid.Column>
            </Grid>
        </Segment>}
        {showModal && <Modal open size="tiny">
            <Modal.Header>
                请输入该习题集的邀请码
            </Modal.Header>
            <Modal.Content>
                <Input fluid value={code} onChange={(_, d) => setCode(d.value)}></Input>
            </Modal.Content>
            <Modal.Actions>
                <Button color="red" onClick={() => setShowModal(false)}>关闭</Button>
                <Button color="green" onClick={doUnlock}>
                    确认
                </Button>
            </Modal.Actions>
        </Modal>}
    </div>;
};

export default ProblemsetList;