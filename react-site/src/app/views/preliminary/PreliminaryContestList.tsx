import React, { useEffect, useState } from "react";
import { Link, useHistory, useParams } from "react-router-dom";
import { Container, Dimmer, Header, Loader, Pagination, Segment, Table } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { useDocumentTitle } from "../../common/Utils";
import preliminaryClient from "./client/PreliminaryClient";
import { PreliminaryContestListEntry } from "./client/types";

const PreliminaryContestList: React.FC<{}> = () => {
    useDocumentTitle("笔试题库");
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<PreliminaryContestListEntry[]>([]);
    const [pageCount, setPageCount] = useState(0);
    const { page: pageStr } = useParams<{ page?: string }>();
    const numberPage = parseInt(pageStr || "1");
    const history = useHistory();
    useEffect(() => {
        (async () => {
            try {
                setLoading(true);
                const { data, pageCount } = await preliminaryClient.getContestList(numberPage);
                setPageCount(pageCount);
                setData(data);
                setLoading(false);
            } catch { } finally { }
        })();
    }, [numberPage]);
    return <>
        <Header as="h1">
            初赛题库
        </Header>
        <Segment>
            {loading && <>
                <div style={{ height: "400px" }}></div>
                <Dimmer active>
                    <Loader></Loader>
                </Dimmer>
            </>}
            {data.length !== 0 && <>
                <Table textAlign="center">
                    <Table.Header>
                        <Table.Row>
                            <Table.HeaderCell>比赛ID</Table.HeaderCell>
                            <Table.HeaderCell>比赛标题</Table.HeaderCell>
                            <Table.HeaderCell>比赛时长</Table.HeaderCell>

                        </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {data.map((item, i) => <Table.Row key={i}>
                            <Table.Cell>{item.id}</Table.Cell>
                            <Table.Cell>
                                <Link to={`${PUBLIC_URL}/preliminary/contest/${item.id}`}>
                                    {item.title}
                                </Link>
                            </Table.Cell>
                            <Table.Cell>
                                {Math.round(item.duration / 60)} 分钟
                            </Table.Cell>
                        </Table.Row>)}
                    </Table.Body>
                </Table>
            </>}
            <Container textAlign="center">
                <Pagination
                    totalPages={pageCount}
                    activePage={numberPage}
                    onPageChange={(_, d) => history.push(`${PUBLIC_URL}/preliminary/list/${d.activePage as number}`)}
                ></Pagination>
            </Container>
        </Segment>
    </>;
};

export default PreliminaryContestList;