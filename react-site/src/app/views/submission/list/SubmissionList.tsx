import QueryString from "qs";
import { useEffect, useMemo, useState } from "react";
import { useHistory, useLocation, useParams } from "react-router";
import { Link } from "react-router-dom";
import { Button, Container, Dimmer, Divider, Header, Loader, Pagination, Segment, Table } from "semantic-ui-react";
import { PUBLIC_URL } from "../../../App";
import { useDocumentTitle } from "../../../common/Utils";
import JudgeStatusLabel from "../../utils/JudgeStatusLabel";
import MemoryCostLabel from "../../utils/MemoryCostLabel";
import ScoreLabel from "../../utils/ScoreLabel";
import UserLink from "../../utils/UserLink";
import submissionClient from "../client/SubmissionClient";
import { SubmissionFilter, SubmissionListEntry } from "../client/types";
import SubmissionFilterArea from "./SubmissionFilterArea";
const validKeys = new Set(["uid", "status", "min_score", "max_score", "problem", "contest"]);
const keyTransformer: { [K in keyof Required<SubmissionFilter>]: (x: string) => NonNullable<SubmissionFilter[K]> } = {
    uid: (x: string) => x,
    status: (x: string) => x as NonNullable<SubmissionFilter["status"]>,
    contest: x => parseInt(x),
    max_score: x => parseInt(x),
    min_score: x => parseInt(x),
    problem: x => parseInt(x)
}
function parseFilter(text: string): SubmissionFilter {
    const filterStr = QueryString.parse(text).filter as (string | undefined) || "";
    const parsed: SubmissionFilter = {};
    try {
        for (const pair of filterStr.split(",")) {
            const [key, value] = pair.split("=");
            if (validKeys.has(key)) {
                const vkey = key as keyof SubmissionFilter;
                (parsed[vkey] as number | string) = keyTransformer[vkey](value);
            }
        }
    } catch {
        return ({});
    }
    return parsed as SubmissionFilter;
};
function encodeFilterToQuertString(filter: SubmissionFilter): string {
    if (Object.keys(filter).length === 0) return "";
    return QueryString.stringify({ filter: Object.entries(filter).filter(x => x[1] !== undefined).map(([key, value]) => `${key}=${value}`).join(",") });
}
const SubmissionList: React.FC<{}> = () => {
    const location = useLocation();
    const params = useParams<{ page: string }>();
    const page = parseInt(params.page);
    const filter = useMemo(() => parseFilter(location.search.substr(1)), [location.search]);
    const [loading, setLoading] = useState(false);
    const [pageCount, setPageCount] = useState(0);
    const [data, setData] = useState<SubmissionListEntry[]>([]);
    const history = useHistory();
    const [showFilter, setShowFilter] = useState(false);

    useDocumentTitle("提交记录列表");
    useEffect(() => {
        (async () => {
            try {
                setLoading(true);
                const resp = await submissionClient.getSubmissionList(page, filter);
                setPageCount(resp.page_count);
                setData(resp.data);
            } catch { } finally {
                setLoading(false);
            }
        })();
    }, [page, filter]);
    return <>
        <Header as="h1">
            提交列表
        </Header>
        {loading && <div style={{ height: "400px" }}>
            <Dimmer active>
                <Loader></Loader>
            </Dimmer>
        </div>}
        {!loading && <Segment stacked>
            <Container textAlign="right">
                <Button size="tiny" color={showFilter ? "blue" : "green"} onClick={() => setShowFilter(c => !c)}>
                    {showFilter ? "隐藏" : "筛选"}
                </Button>
            </Container>
            {showFilter && <>
                <SubmissionFilterArea
                    defaultFilter={filter}
                    onUpdate={d => history.push(`${PUBLIC_URL}/submissions/${page}?${encodeFilterToQuertString(d)}`)}
                ></SubmissionFilterArea>
                <Divider></Divider>
            </>}
            <Table basic="very">
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell textAlign="center" style={{ maxWidth: "80px", width: "80px" }}>提交ID</Table.HeaderCell>
                        <Table.HeaderCell textAlign="center">题目</Table.HeaderCell>
                        <Table.HeaderCell>用户</Table.HeaderCell>
                        <Table.HeaderCell>提交时间</Table.HeaderCell>
                        <Table.HeaderCell>时间占用</Table.HeaderCell>
                        <Table.HeaderCell>空间占用</Table.HeaderCell>
                        <Table.HeaderCell textAlign="center">状态</Table.HeaderCell>
                        <Table.HeaderCell>分数</Table.HeaderCell>
                        <Table.HeaderCell>比赛</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {data.map((x, i) => <Table.Row key={i}>
                        <Table.Cell textAlign="center">
                            <Link to={`${PUBLIC_URL}/show_submission/${x.id}`}>{x.id}</Link>
                        </Table.Cell>
                        <Table.Cell textAlign="center" style={{ maxWidth: "350px" }}>
                            <Link to={`${PUBLIC_URL}/show_problem/${x.problem_id}`}>#{x.problem_id}. {x.problem_title}</Link>
                        </Table.Cell>
                        <Table.Cell>
                            <UserLink data={x}></UserLink>
                        </Table.Cell>
                        <Table.Cell>
                            {x.submit_time}
                        </Table.Cell>
                        <Table.Cell>
                            {x.time_cost} ms
                        </Table.Cell>
                        <Table.Cell>
                            <MemoryCostLabel memoryCost={x.memory_cost}></MemoryCostLabel>
                        </Table.Cell>
                        <Table.Cell textAlign="center">
                            <Link to={`${PUBLIC_URL}/show_submission/${x.id}`}>
                                <JudgeStatusLabel status={x.status}></JudgeStatusLabel>
                            </Link>
                        </Table.Cell>
                        <Table.Cell>
                            {x.status !== "invisible" && <Link to={`${PUBLIC_URL}/show_submission/${x.id}`}>
                                <ScoreLabel score={x.score} fullScore={x.total_score}></ScoreLabel>
                            </Link>}
                        </Table.Cell>
                        <Table.Cell>
                            {x.contest !== -1 && <Link to={`${PUBLIC_URL}/contest/${x.contest}`}>{x.contest}</Link>}
                        </Table.Cell>
                    </Table.Row>)}
                </Table.Body>
            </Table>
            <Container textAlign="center">
                <Pagination
                    totalPages={pageCount}
                    activePage={page}
                    onPageChange={(e, d) => {
                        history.push(`${PUBLIC_URL}/submissions/${d.activePage}?${encodeFilterToQuertString(filter)}`);
                    }}
                ></Pagination>
            </Container>
        </Segment>}
    </>;
};

export default SubmissionList;