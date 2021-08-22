import { DateTime } from "luxon";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Button, Dimmer, Grid, Header, Loader, Pagination, Segment, Table } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { useDocumentTitle } from "../../common/Utils";
import { VirtualContestEntry } from "./client/types";
import virtualContestClient from "./client/VirtualcontestClient";

function makeStatus(start: number, end: number): [{ positive?: true; negative?: true; }, string] {
    const now = DateTime.now().toSeconds();
    if (now < start) return [{}, "尚未开始"];
    if (now >= start && now <= end) return [{ positive: true }, "正在进行中"];
    else return [{ negative: true }, "已结束"]
}

function timeToString(s: number): string {
    return DateTime.fromSeconds(s).toJSDate().toLocaleString();
}
const VirtualContestList: React.FC<{}> = () => {
    useDocumentTitle("虚拟比赛列表");
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<VirtualContestEntry[]>([]);
    const [page, setPage] = useState(0);
    const [pageCount, setPageCount] = useState(0);
    const [loaded, setLoaded] = useState(false);
    const loadPage = async (page: number) => {
        try {
            setLoading(true);
            const resp = await virtualContestClient.getVirtualContestList(page);
            setPageCount(resp.pageCount);
            setData(resp.data);
            setPage(page);
            setLoaded(true);
        } catch (e: any) { console.error(e); }
        finally {
            setLoading(false);
        }
    }
    useEffect(() => {
        if (!loaded) {
            loadPage(1);
        }
    }, [loaded]);

    return <>
        {loading && data.length === 0 && <div style={{ height: "400px" }}></div>}
        {loading && <Dimmer active>
            <Loader></Loader>
        </Dimmer>}
        {loaded && <>
            <Header as="h1">
                虚拟比赛列表
            </Header>
            <Segment stacked>
                <Table textAlign="center">
                    <Table.Header>
                        <Table.Row>
                            <Table.HeaderCell>ID</Table.HeaderCell>
                            <Table.HeaderCell>原始比赛</Table.HeaderCell>
                            <Table.HeaderCell>开始时间</Table.HeaderCell>
                            <Table.HeaderCell>结束时间</Table.HeaderCell>
                            <Table.HeaderCell>状态</Table.HeaderCell>
                            <Table.HeaderCell>操作</Table.HeaderCell>
                        </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {data.map((x, i) => {
                            const [status, text] = makeStatus(x.startTime, x.endTime);
                            return <Table.Row key={i}>
                                <Table.Cell>{x.id}</Table.Cell>
                                <Table.Cell>
                                    <Link to={`${PUBLIC_URL}/contest/${x.contest.id}`}>#{x.contest.id}. {x.contest.name}</Link>
                                </Table.Cell>
                                <Table.Cell>{timeToString(x.startTime)}</Table.Cell>
                                <Table.Cell>{timeToString(x.endTime)}</Table.Cell>
                                <Table.Cell {...status}>{text}</Table.Cell>
                                <Table.Cell>
                                    <Button size="tiny" color="green" as={Link} to={`${PUBLIC_URL}/contest/${x.contest.id}?virtual_contest=${x.id}`}>
                                        前往
                                    </Button>
                                </Table.Cell>
                            </Table.Row>;
                        })}
                    </Table.Body>
                </Table>
                <Grid columns="3" centered>
                    <Grid.Column>
                        <Pagination
                            totalPages={pageCount}
                            activePage={page}
                            onPageChange={(e, d) => loadPage(d.activePage as number)}
                        ></Pagination>
                    </Grid.Column>
                </Grid>
            </Segment>
        </>}
    </>;
};

export default VirtualContestList;