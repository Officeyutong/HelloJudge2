import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { useHistory, useParams } from "react-router";
import { Link } from "react-router-dom";
import { Container, Dimmer, Divider, Header, Loader, Pagination, Segment, Table } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { toLocalTime, useCurrentUid, useDocumentTitle } from "../../common/Utils";
import { StateType } from "../../states/Manager";
import UserLink from "../utils/UserLink";
import discussionClient from "./client/DiscussionClient";
import { DiscussionEntry } from "./client/types";
import DiscussionEdit from "./DiscussionEdit";

const DiscussionList: React.FC<{}> = () => {
    const { path, page } = useParams<{ path: string; page: string; }>();
    const [loadingCount, setLoadingCount] = useState(0);
    const [pathDisplay, setPathDisplay] = useState("");
    const [data, setData] = useState<DiscussionEntry[]>([]);
    const [pageCount, setPageCount] = useState(0);
    const [managable, setManagable] = useState(false);
    const numberPage = parseInt(page);
    const alreadyLogin = useSelector((s: StateType) => s.userState.login);
    const currUser = useCurrentUid();
    const history = useHistory();
    const [editing, setEditing] = useState(false);
    const [editID, setEditID] = useState(-1);
    const [dummy, setDummy] = useState(false);
    useEffect(() => {
        (async () => {
            try {
                setLoadingCount(c => c + 1);
                const resp = await discussionClient.getPathName(path);
                setPathDisplay(resp);
                setLoadingCount(c => c - 1);
            } catch { } finally { }
        })();
    }, [path]);
    useEffect(() => {
        (async () => {
            try {
                setLoadingCount(c => c + 1);
                const resp = await discussionClient.getDiscussions(path, numberPage, 1e6);
                setManagable(resp.managable);
                setPageCount(resp.page_count);
                setData(resp.data);
                setLoadingCount(c => c - 1);
            } catch { } finally { }
        })();
    }, [numberPage, path, dummy]);
    useDocumentTitle(`${loadingCount === 0 ? pathDisplay + ' - 讨论列表' : '加载中...'}`)
    const editDiscussion = (id: number) => {
        setEditID(id);
        setEditing(true);
    };
    const removeDiscussion = (id: number) => {
        discussionClient.removeDiscussion(id).then(resp => {
            setDummy(d => !d);
        });
    };
    const finishCallback = () => {
        setDummy(d => !d);
    };
    return <>
        {loadingCount !== 0 && <Segment stacked>
            <div style={{ height: "400px" }}></div>
            <Dimmer active>
                <Loader></Loader>
            </Dimmer>
        </Segment>}
        {loadingCount === 0 && <>
            <Header as="h2">
                {pathDisplay}
            </Header>
            <Segment stacked>
                <Table basic="very">
                    <Table.Header>
                        <Table.Row>
                            <Table.HeaderCell textAlign="center">标题</Table.HeaderCell>
                            <Table.HeaderCell textAlign="center">发布者</Table.HeaderCell>
                            <Table.HeaderCell textAlign="center">时间</Table.HeaderCell>
                            <Table.HeaderCell textAlign="center">回复数</Table.HeaderCell>
                            <Table.HeaderCell textAlign="center">最新回复于</Table.HeaderCell>
                            <Table.HeaderCell textAlign="center">操作</Table.HeaderCell>
                        </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {data.map((item, i) => <Table.Row key={i}>
                            <Table.Cell style={{ width: "300px" }} textAlign="center">
                                <Link to={`${PUBLIC_URL}/show_discussion/${item.id}`}>{item.title}</Link>
                                {/* <a href={`/show_discussion/${item.id}`}>{item.title}</a> */}
                            </Table.Cell>
                            <Table.Cell textAlign="center">
                                <UserLink data={{ uid: item.uid, username: item.username }}></UserLink>
                            </Table.Cell>
                            <Table.Cell textAlign="center">
                                {toLocalTime(item.time)}
                            </Table.Cell>
                            <Table.Cell textAlign="center">
                                {item.comment_count}
                            </Table.Cell>
                            <Table.Cell textAlign="center">
                                {item.last_comment_time && toLocalTime(item.last_comment_time)}
                            </Table.Cell>
                            {(managable || currUser === item.uid) && <Table.Cell textAlign="center">
                                {
                                    // eslint-disable-next-line jsx-a11y/anchor-is-valid
                                    <a onClick={() => editDiscussion(item.id)}>编辑</a>
                                }
                                <div style={{ width: "5px", display: "inline" }}> </div>
                                {
                                    // eslint-disable-next-line jsx-a11y/anchor-is-valid
                                    <a onClick={() => removeDiscussion(item.id)}>删除</a>
                                }
                            </Table.Cell>}
                        </Table.Row>)}
                    </Table.Body>
                </Table>
                <Container textAlign="center">
                    <Pagination
                        totalPages={pageCount}
                        activePage={numberPage}
                        onPageChange={(_, d) => history.push(`${PUBLIC_URL}/discussions/${path}/${d.activePage}`)}
                    ></Pagination>
                </Container>
            </Segment>
            {alreadyLogin && <>
                <Divider></Divider>
                <Header as="h3">
                    {editing ? "编辑讨论" : "发布新讨论"}
                </Header>
                <DiscussionEdit
                    edit={editing}
                    finishCallback={finishCallback}
                    id={editID}
                    path={path}
                ></DiscussionEdit>
            </>}
        </>}
    </>;
};

export default DiscussionList;