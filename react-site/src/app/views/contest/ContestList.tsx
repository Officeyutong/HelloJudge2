import { Schema, validate } from "jsonschema";
import { DateTime } from "luxon";
import QueryString from "qs";
import React, { useEffect, useMemo, useState } from "react";
import { useHistory, useLocation, useParams } from "react-router";
import { Link } from "react-router-dom";
import { Button, Container, Dimmer, Divider, Dropdown, Form, Grid, Header, Icon, Loader, Pagination, Segment, Table } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { ButtonClickEvent } from "../../common/types";
import { useDocumentTitle } from "../../common/Utils";
import { showErrorModal } from "../../dialogs/Dialog";
import UserLink from "../utils/UserLink";
import contestClient from "./client/ContestClient";
import { ContestListResponse, ContestSortingOrder, ContestSortingOrderMapping } from "./client/types";

interface ContestListOption {
    order_by: ContestSortingOrder;
};
const OptionSchema: Schema = {
    id: "ContestListOptionSchema",
    type: "object",
    properties: {
        order_by: {
            type: "string",
            enum: ["id", "start_time"]
        }
    },
    required: ["order_by"]
};
function decodeContestListOption(str: string): ContestListOption {
    const parsed = QueryString.parse(str).option as string;
    let jsonObj;
    try {
        jsonObj = JSON.parse(parsed);
    } catch {
        return { order_by: "start_time" };
    }
    const validRet = validate(jsonObj, OptionSchema);
    if (!validRet.valid) return { order_by: "start_time" };
    return jsonObj as ContestListOption;
}
function encodeContestListOption(option: ContestListOption) {
    if (option.order_by === "start_time") return "";
    return QueryString.stringify({ option: JSON.stringify(option) });
}
function runningCheck(start: number, end: number): boolean {
    const now = DateTime.now().toSeconds();
    return (now >= start && now <= end);
}
function transformToString(second: number): string {
    return DateTime.fromSeconds(second).toJSDate().toLocaleString();
}
const ContestList: React.FC<{}> = () => {
    const { page } = useParams<{ page: string }>();
    const numberPage = parseInt(page);
    const location = useLocation();
    const queryString = location.search;
    const option = useMemo(() => decodeContestListOption(queryString.substr(1)), [queryString]);
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<ContestListResponse | null>(null);
    const history = useHistory();
    useDocumentTitle("比赛列表");
    useEffect(() => {
        (async () => {
            try {
                setLoading(true);
                const resp = await contestClient.getContestList(numberPage, option.order_by);
                setData(resp);
            } catch (e: any) {
                showErrorModal(e.message);
            } finally {
                setLoading(false);
            }
        })();
    }, [numberPage, option]);
    const createContest = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            const { contest_id } = await contestClient.createContest();
            window.open(`/contest/${contest_id}`);
        } catch (e: any) {
            showErrorModal(e.message);
        } finally {
            target.classList.remove("loading");
        }
    };
    return <>
        <Header as="h1">
            比赛列表
        </Header>
        <Segment stacked>
            {loading && <Dimmer active>
                <Loader></Loader></Dimmer>}
            <Grid columns="2">
                <Grid.Column>
                    <Form >
                        <Form.Field width="3">
                            <label>排序方式</label>
                            <Dropdown selection options={[{ text: ContestSortingOrderMapping["start_time"], value: "start_time" }, { text: ContestSortingOrderMapping["id"], value: "id" }]} text={ContestSortingOrderMapping[option.order_by]} onChange={(e, d) => {
                                history.push(`${PUBLIC_URL}/contests/1?${encodeContestListOption({ order_by: d.value as ContestSortingOrder })}`);
                            }}></Dropdown>
                        </Form.Field>
                    </Form>
                </Grid.Column>
                <Grid.Column>
                    <Container textAlign="right">
                        <Button color="green" icon onClick={createContest}>
                            <Icon name="plus"></Icon>
                            添加比赛...
                        </Button>
                    </Container>
                </Grid.Column>
            </Grid>
            <Divider></Divider>
            {!loading && <>
                <Table basic="very">
                    <Table.Header>
                        <Table.Row>
                            <Table.HeaderCell textAlign="center">比赛名</Table.HeaderCell>
                            <Table.HeaderCell textAlign="center">创建者</Table.HeaderCell>
                            <Table.HeaderCell textAlign="center">权限</Table.HeaderCell>
                            <Table.HeaderCell textAlign="center">开始时间</Table.HeaderCell>
                            <Table.HeaderCell textAlign="center">结束时间</Table.HeaderCell>
                        </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {(data?.list || []).map((x, i) => <Table.Row
                            positive={runningCheck(x.start_time, x.end_time)}
                            key={i}>
                            <Table.Cell textAlign="center">
                                {/* <a target="_blank" rel="noreferrer" href={`/contest/${x.id}`}>{x.id}. {x.name}</a> */}
                                <Link to={`${PUBLIC_URL}/contest/${x.id}`}>{x.id}. {x.name}</Link>
                            </Table.Cell>
                            <Table.Cell textAlign="center">
                                <UserLink data={{ uid: x.owner_id, username: x.owner_username }}></UserLink>
                            </Table.Cell>
                            <Table.Cell textAlign="center" positive={x.privateContest || x.hasPermission}>
                                {x.privateContest ? <div>
                                    <Icon name={x.hasPermission ? "lock open" : "lock"}></Icon>
                                </div> : <div>
                                    公开比赛
                                </div>}
                            </Table.Cell>
                            <Table.Cell textAlign="center">
                                {transformToString(x.start_time)}
                            </Table.Cell>
                            <Table.Cell textAlign="center">
                                {transformToString(x.end_time)}
                            </Table.Cell>
                        </Table.Row>)}
                    </Table.Body>
                </Table>
                <Grid columns="3" centered>
                    <Grid.Column>
                        <Pagination
                            totalPages={data?.page_count || 0}
                            activePage={numberPage}
                            onPageChange={(e, d) => history.push(`${PUBLIC_URL}/contests/${d.activePage}?${encodeContestListOption(option)}`)}
                        ></Pagination>
                    </Grid.Column>
                </Grid>
            </>}
        </Segment>
    </>;
};

export default ContestList;