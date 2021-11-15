import { Schema, validate } from "jsonschema";
import QueryString, { ParsedQs } from "qs";
import React, { useEffect, useMemo, useState } from "react";
import { useHistory, useLocation, useParams } from "react-router";
import { Link } from "react-router-dom";
import { Button, Container, Dimmer, Divider, Header, Icon, Loader, Pagination, Segment, Table } from "semantic-ui-react";
import { PUBLIC_URL } from "../../../App";
import { ButtonClickEvent, ProblemTagEntry } from "../../../common/types";
import { useDocumentTitle } from "../../../common/Utils";
import problemClient from "../client/ProblemClient";
import { ProblemListEntry, ProblemSearchFilter } from "../client/types";
import qs from "qs";
import ProblemTagLabel from "../../utils/ProblemTagLabel";
import ProblemFilter from "./ProblemFilter";
import { showErrorModal } from "../../../dialogs/Dialog";
const ProblemFilterSchema: Schema = {
    id: "ProblemFilter",
    type: "object",
    properties: {
        tag: {
            type: "array",
            items: {
                type: "string"
            }
        },
        searchKeyword: {
            type: "string"
        }
    }
};
function parseFilter(text: string): ProblemSearchFilter {
    let filter: ProblemSearchFilter;
    try {
        const query = QueryString.parse(text) as ParsedQs;

        filter = JSON.parse((query.filter as string) || "{}");
    } catch {
        filter = {};
    }
    {

        const ret = validate(filter, ProblemFilterSchema);
        if (!ret.valid) filter = {};
    }
    return filter;
}
// (window as (typeof window ) & {qs:any}).qs=qs;
function encodeFilter(filter: ProblemSearchFilter): string {
    const encoded = JSON.stringify(filter);
    return qs.stringify({
        filter: encoded === "{}" ? undefined : encoded
    });
}
const ProblemList: React.FC<{}> = () => {
    const { page } = useParams<{ page: string }>();
    const numberPage = parseInt(page);
    const history = useHistory();
    const location = useLocation();
    const [filter, setFilter] = useState(parseFilter(location.search.substr(1)));
    const [loading, setLoading] = useState(false);
    const [pageCount, setPageCount] = useState(0);
    const [data, setData] = useState<ProblemListEntry[]>([]);
    const [allTags, setAllTags] = useState<ProblemTagEntry[]>([]);
    const [tagsLoaded, setTagsLoaded] = useState(false);
    const tagMapping = useMemo(() => new Map(allTags.map(x => ([x.id, x]))), [allTags]);
    useDocumentTitle("题目列表");
    useEffect(() => {
        if (!tagsLoaded) {
            problemClient.getProblemtags().then(resp => {
                setAllTags(resp);
                setTagsLoaded(true);
            })
        }
    }, [tagsLoaded]);
    useEffect(() => {
        (async () => {
            try {
                setLoading(true);
                const resp = await problemClient.getProblemList(
                    numberPage, filter
                );
                if (resp.code !== 0) {
                    showErrorModal(resp.message);
                    return;
                }
                setData(resp.data);
                setPageCount(resp.pageCount);
            } catch { } finally {
                setLoading(false);
            }
        })();
    }, [numberPage, filter]);
    const createProblem = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            const { problem_id } = await problemClient.createProblem();
            window.open(`/show_problem/${problem_id}`);
        } catch { } finally {
            target.classList.remove("loading");
        }
    };
    return <div>
        <Header as="h1">
            题库
        </Header>
        <Segment stacked>
            {loading && <Dimmer active> <Loader></Loader></Dimmer>}
            <Container textAlign="right">
                <Button as={Link} color="green" icon to={`${PUBLIC_URL}/tags/edit`} >
                    <Icon name="plus"></Icon>题目标签编辑
                </Button>
                <Button as={Link} color="blue" icon to={`${PUBLIC_URL}/import_from_syzoj`}>
                    <Icon name="plus"></Icon> 从SYZOJ导入题目
                </Button>
                <Button onClick={createProblem} icon color="green">
                    <Icon name="plus"></Icon> 创建题目
                </Button>
            </Container>
            <ProblemFilter
                allTags={allTags}
                filter={filter}
                update={f => {
                    history.push(`${PUBLIC_URL}/problems/1?${encodeFilter(f)}`);
                    setFilter(f);
                }}
            ></ProblemFilter>
            <Divider></Divider>
            <Table basic="very">
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell style={{ maxWidth: "80px", width: "80px" }} textAlign="center">
                            题目编号
                        </Table.HeaderCell>
                        <Table.HeaderCell>
                            题目标题
                        </Table.HeaderCell>
                        <Table.HeaderCell>
                            标签
                        </Table.HeaderCell>
                        <Table.HeaderCell>
                            通过数
                        </Table.HeaderCell>
                        <Table.HeaderCell>
                            提交数
                        </Table.HeaderCell>
                        <Table.HeaderCell>
                            通过率
                        </Table.HeaderCell>
                        <Table.HeaderCell>
                            我的提交
                        </Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {data.map((x, i) => <Table.Row
                        positive={x.mySubmission.id !== -1 && x.mySubmission.status === "accepted"}
                        negative={x.mySubmission.id !== -1 && x.mySubmission.status === "unaccepted"}
                        key={i}>
                        <Table.Cell textAlign="center" style={{ maxWidth: "80px", width: "80px" }}>{x.id}</Table.Cell>
                        <Table.Cell style={{ minWidth: "300px" }}>
                            <Link to={`${PUBLIC_URL}/show_problem/${x.id}`} style={{ color: !x.public ? "green" : undefined }}>
                                {x.title}
                            </Link>
                        </Table.Cell>
                        <Table.Cell>
                            <div style={{ maxWidth: "300px", overflowWrap: "break-word" }}>
                                {x.tags.map(y => <ProblemTagLabel
                                    key={y}
                                    data={tagMapping.has(y) ? tagMapping.get(y)! : { color: "black", display: y }}
                                ></ProblemTagLabel>)}
                            </div>
                        </Table.Cell>
                        <Table.Cell>
                            {x.acceptedSubmit}
                        </Table.Cell>
                        <Table.Cell>
                            {x.totalSubmit}
                        </Table.Cell>
                        <Table.Cell>
                            {x.totalSubmit === 0 ? "无提交" : `${Math.ceil(100 * x.acceptedSubmit / x.totalSubmit)}%`}
                        </Table.Cell>
                        <Table.Cell>
                            {/* {x.mySubmission.id !== -1 && <Link to={`${PUBLIC_URL}/show_submission/${x.mySubmission.id}`}>
                                {x.mySubmission.id}
                            </Link>} */}
                            {x.mySubmission.id !== -1 && <a href={`/show_submission/${x.mySubmission.id}`}>
                                {x.mySubmission.id}
                            </a>}
                        </Table.Cell>
                    </Table.Row>)}
                </Table.Body>
            </Table>
            <Container textAlign="center">
                <Pagination
                    totalPages={pageCount}
                    activePage={numberPage}
                    onPageChange={(e, d) => history.push(`${PUBLIC_URL}/problems/${d.activePage}?${encodeFilter(filter)}`)}
                ></Pagination>
            </Container>
        </Segment>
    </div>;
};

export default ProblemList;