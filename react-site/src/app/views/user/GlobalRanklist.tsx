import { Schema, validate } from "jsonschema";
import QueryString, { ParsedQs } from "qs";
import React, { useEffect, useState } from "react";
import { useHistory, useLocation, useParams } from "react-router-dom";
import { Container, Dimmer, Divider, Header, Input, Loader, Pagination, Segment, Table } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { Markdown } from "../../common/Markdown";
import { KeyDownEvent } from "../../common/types";
import { useDocumentTitle, useInputValue } from "../../common/Utils";
import UserLink from "../utils/UserLink";
import { GlobalRanklistItem } from "./client/types";
import userClient from "./client/UserClient";

interface RanklistFilter {
    text?: string;
};
const RanklistSchema: Schema = {
    type: "object",
    properties: {
        text: { type: "string" }
    }
};
function parseFilter(text: string): RanklistFilter {
    let filter: RanklistFilter;
    try {
        const query = QueryString.parse(text) as ParsedQs;

        filter = JSON.parse((query.filter as string) || "{}");
    } catch {
        filter = {};
    }
    if (!validate(filter, RanklistSchema).valid) filter = {};
    return filter;
};
function encodeFilter(filter: RanklistFilter): string {
    const encoded = JSON.stringify(filter);
    const ret = QueryString.stringify({
        filter: encoded === "{}" ? undefined : encoded
    });
    return ret === "" ? "" : "?" + ret;
}
const GlobalRanklist: React.FC<{}> = () => {
    const { page } = useParams<{ page: string }>();
    const numberPage = parseInt(page);
    const history = useHistory();
    const location = useLocation();
    const [data, setData] = useState<GlobalRanklistItem[]>([]);
    const [loading, setLoading] = useState(false);
    const [filter, setFilter] = useState(parseFilter(location.search.substr(1)));
    const [pageCount, setPageCount] = useState(0);
    const currSearch = useInputValue(filter.text || "");
    useDocumentTitle("全局排行榜");
    useEffect(() => {
        (async () => {
            try {
                setLoading(true);
                const resp = await userClient.getGlobalRanklist(numberPage, filter.text);
                setData(resp.ranklist);
                setPageCount(resp.pageCount);
                setLoading(false);
            } catch { } finally { }
        })();
    }, [numberPage, filter]);
    return <>
        <Header as="h1">
            排行榜
        </Header>
        <Segment stacked>
            {loading && <Dimmer active>
                <Loader></Loader>
            </Dimmer>}
            <Container textAlign="right">
                <Input icon="search" placeholder="按回车进行搜索..." onKeyDown={(e: KeyDownEvent) => {
                    if (e.code === "Enter") {
                        history.push(`${PUBLIC_URL}/ranklist/${numberPage}${encodeFilter({
                            text: e.currentTarget.value
                        })}`);
                        setFilter({
                            text: e.currentTarget.value
                        });
                    }
                }} {...currSearch}></Input>
            </Container>
            <Divider></Divider>
            <Table
                basic="very"
                celled
            >
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell textAlign="center">用户名</Table.HeaderCell>
                        <Table.HeaderCell textAlign="center">个人简介</Table.HeaderCell>
                        <Table.HeaderCell textAlign="center">Rating</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {data.map((x, i) => <Table.Row key={i}>
                        <Table.Cell textAlign="center">
                            <UserLink data={{ uid: x.uid, username: x.username }}></UserLink>
                        </Table.Cell>
                        <Table.Cell textAlign="center">
                            <div style={{ maxHeight: "50px", overflowY: "hidden", overflowX: "hidden", maxWidth: "700px" }}>
                                <Markdown markdown={x.description}></Markdown>
                            </div>
                        </Table.Cell>
                        <Table.Cell textAlign="center">
                            {x.rating}
                        </Table.Cell>
                    </Table.Row>)}
                </Table.Body>
            </Table>
            <Container textAlign="center">
                <Pagination
                    totalPages={pageCount}
                    activePage={numberPage}
                    onPageChange={(_, d) => history.push(`${PUBLIC_URL}/ranklist/${d.activePage}${encodeFilter(filter)}`)}
                ></Pagination>
            </Container>
        </Segment>
    </>;
};

export default GlobalRanklist;