import React, { useCallback, useEffect, useState } from "react";
import { Button, Checkbox, Dimmer, Divider, Form, Grid, Header, Icon, Input, Loader, Pagination, Segment, Table } from "semantic-ui-react";
import { showSuccessPopup } from "../../../dialogs/Utils";
import { adminClient } from "../client/AdminClient";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-markdown";
import "ace-builds/src-noconflict/theme-github";
import { Markdown } from "../../../common/Markdown";
import { FeedList } from "../client/types";
const FeedManagement: React.FC<{}> = () => {
    const [loading, setLoading] = useState(false);
    const [feedID, setFeedID] = useState("");
    const [content, setContent] = useState("");
    const [top, setTop] = useState(false);
    const [dummy, setDummy] = useState(false);
    const removeFeed = useCallback(async () => {
        try {
            setLoading(true);
            await adminClient.removeFeed(parseInt(feedID));
            showSuccessPopup("删除成功!");
        } catch (e) { } finally { setLoading(false); }
    }, [feedID]);
    const sendFeed = useCallback(async () => {
        try {
            setLoading(true);
            await adminClient.sendGlobalFeed(top, content);
            showSuccessPopup("发送成功！");
            setDummy(c => !c);
        } catch (e) { } finally {
            setLoading(false);
        }
    }, [top, content]);
    return <div>
        <Dimmer active={loading}>
            <Loader>加载中</Loader>
        </Dimmer>
        <Header as="h3">
            删除推送
        </Header>
        <Form>
            <Form.Field>
                <label>Feed ID</label>
                <Input value={feedID} onChange={(_, d) => setFeedID(d.value)}></Input>
            </Form.Field>
            <Form.Button color="red" onClick={removeFeed}>
                删除
            </Form.Button>
        </Form>
        <Divider></Divider>
        <div >
            <Header as="h3">
                发送全局推送
            </Header>
            <Form>
                <Form.Field>
                    <Grid columns="2" centered>
                        <Grid.Column>
                            <AceEditor
                                value={content}
                                onChange={v => setContent(v)}
                                mode="markdown"
                                theme="github"
                                height="300px"
                                width="100%"
                            ></AceEditor>
                        </Grid.Column>
                        <Grid.Column>
                            <Segment style={{ maxHeight: "300px", overflowY: "scroll" }}>
                                <Markdown markdown={content}></Markdown>
                            </Segment>
                        </Grid.Column>
                    </Grid>
                </Form.Field>
                <Form.Field>
                    <Checkbox toggle label="置顶" checked={top} onChange={(_, d) => setTop(d.checked!)}></Checkbox>

                </Form.Field>
                <Form.Field>

                    <Button labelPosition="right" icon color="green" onClick={sendFeed}>
                        <Icon name="paper plane outline"></Icon>
                        发送</Button>
                </Form.Field>
            </Form>
        </div>
        <Divider></Divider>
        <GlobalFeedList dummy={dummy}></GlobalFeedList>
    </div>;
};

const GlobalFeedList: React.FC<{ dummy: boolean }> = ({ dummy }) => {
    const [page, setPage] = useState(1);
    const [pageCount, setPageCount] = useState(-1);
    const [loaded, setLoaded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<FeedList | null>(null);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                await loadPage(1);
            })();
        }
    }, [loaded, page]);
    useEffect(() => {
        if (loaded) {
            loadPage(1);
        }
    }, [dummy, loaded])
    const loadPage = async (page: number) => {
        try {
            setLoading(true);
            const resp = await adminClient.getGlobalFeed(page);
            setData(resp.data);
            setPageCount(resp.pageCount);
            setPage(page);
            setLoaded(true);
        } catch (e) { } finally {
            setLoading(false);
        }
    };
    const removeFeed = async (id: number) => {
        try {
            setLoading(true);
            await adminClient.removeFeed(id);
            await loadPage(page);
            showSuccessPopup("删除成功!");
        } catch (e) { } finally { setLoading(false); }
    };
    return <div>
        {loading && <>
            <Dimmer active={loading}>
                <Loader>加载中...</Loader>
            </Dimmer>
            <div style={{ height: "400px" }}></div>
        </>}
        {loaded && <div>
            <Table>
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell>推送ID</Table.HeaderCell>
                        <Table.HeaderCell>发送时间</Table.HeaderCell>
                        <Table.HeaderCell>是否置顶</Table.HeaderCell>
                        <Table.HeaderCell>内容</Table.HeaderCell>
                        <Table.HeaderCell>操作</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {data!.map((x, i) => <Table.Row key={i}>
                        <Table.Cell>{x.id}</Table.Cell>
                        <Table.Cell>{x.time}</Table.Cell>
                        <Table.Cell>
                            {x.top ? <Icon name="check" color="green"></Icon> : <Icon name="times" color="red"></Icon>}
                        </Table.Cell>
                        <Table.Cell>{x.content}</Table.Cell>
                        <Table.Cell><Button color="red" size="tiny" onClick={() => removeFeed(x.id)}>删除</Button></Table.Cell>
                    </Table.Row>)}
                </Table.Body>
            </Table>
            <Grid columns="3" centered>
                <Grid.Column>
                    <Pagination
                        totalPages={pageCount}
                        activePage={page}
                        onPageChange={(_, d) => loadPage(d.activePage as number)}
                    ></Pagination>
                </Grid.Column>
            </Grid>
        </div>}
    </div>;
};

export default FeedManagement;