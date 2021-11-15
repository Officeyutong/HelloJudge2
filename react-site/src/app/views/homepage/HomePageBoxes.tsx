import { useCallback, useEffect, useState } from "react";
import { useSelector } from "react-redux";
import { useHistory } from "react-router";
import { Button, Dimmer, Divider, Grid, Header, Icon, Input, List, Loader, Segment } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { StateType } from "../../states/Manager";
import discussionClient from "../discussion/client/DiscussionClient";
import { DiscussionEntry } from "../discussion/client/types";
import problemtodoClient from "../problemtodo/client/ProblemtodoClient";
import { ProblemtodoEntry } from "../problemtodo/client/types";
import JudgeStatusLabel from "../utils/JudgeStatusLabel";
import { FriendLinkEntry, ToolBoxEntry } from "./client/types";

const BroadcastBox: React.FC<{}> = () => {
    const [loading, setLoading] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<DiscussionEntry[]>([]);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setLoading(true);
                    setData(await (await discussionClient.getDiscussions("broadcast", 1, 5)).data);
                    setLoaded(true);
                } catch (e) { } finally {
                    setLoading(false);
                }
            })();
        }
    }, [loaded]);
    return <Segment stacked>
        {loading && <Dimmer active={loading}>
            <Loader></Loader>
        </Dimmer>}
        <Header as="h3">
            公告
        </Header>
        <List>
            {data.map((x, i) => <List.Item key={i}>
                <a href={`/show_discussion/${x.id}`} target="_blank" rel="noreferrer">
                    {x.title}
                </a>
            </List.Item>)}
            <Divider></Divider>
            <List.Item>
                <a href="/discussions/broadcast/1" target="_blank" rel="noreferrer">
                    查看全部...
                </a>
            </List.Item>
        </List>
    </Segment>;
};

const ProblemtodoBox: React.FC<{}> = () => {
    const [loading, setLoading] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<ProblemtodoEntry[]>([]);
    const alreadyLoding = useSelector((s: StateType) => s.userState.login);
    useEffect(() => {
        if (!loaded && alreadyLoding) {
            (async () => {
                try {
                    setLoading(true);
                    setData(await problemtodoClient.getAll());
                    setLoaded(true);
                } catch (e) { } finally {
                    setLoading(false);
                }
            })();
        }
    }, [loaded, alreadyLoding]);
    return <Segment stacked>
        {loading && <Dimmer active={loading}>
            <Loader></Loader>
        </Dimmer>}
        <Header as="h3">
            我的待做题目
        </Header>
        <a href="/problemtodo/list" target="_blank" rel="noreferrer">管理</a>
        <Divider></Divider>
        {data.length === 0 ? <div>还没有题...</div> : <div>
            <List>
                {data.map((x, i) => <List.Item key={i}>
                    <a href={x.submission.id === -1 ? undefined : `/show_submission/${x.submission.id}`} target="_blank" rel="noreferrer">
                        <JudgeStatusLabel showText={false} status={x.submission.status}></JudgeStatusLabel>
                    </a>
                    <a href={`/show_problem/${x.id}`} target="_blank" rel="noreferrer">#{x.id}. {x.title}</a>
                </List.Item>)}
            </List>
        </div>}
    </Segment>
};


const FriendLinkBox: React.FC<{ data: FriendLinkEntry[] }> = ({ data }) => {
    return <Segment stacked>
        <Header as="h3">
            友情链接
        </Header>
        <List>
            {data.map((x, i) => <List.Item key={i}>
                <a target="_blank" href={x.url} rel="noreferrer">{x.name}</a>
            </List.Item>)}
        </List>
    </Segment>
};
const ToolBox: React.FC<{ data: ToolBoxEntry[] }> = ({ data }) => {
    return <Segment stacked>
        <Header as="h3">
            工具箱
        </Header>
        <Grid centered columns="2">
            {data.map((x, i) => <Grid.Column key={i}>
                <Button color={x.color} size="tiny" onClick={() => window.open(x.url)}>{x.name}</Button>
            </Grid.Column>)}
        </Grid>
    </Segment>
};
const ProblemSearchBox: React.FC<{}> = () => {
    const [text, setText] = useState("");
    const history = useHistory();
    const doSearch = useCallback(() => {
        if (text) {
            history.push(`${PUBLIC_URL}/problems/1?filter=${encodeURIComponent(JSON.stringify({ searchKeyword: text }))}`);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [text]);
    return <Segment stacked>
        <Header as="h3">题目搜索</Header>
        <Input fluid placeholder="按回车键发起搜索..." value={text} onChange={(_, d) => setText(d.value)} onKeyDown={((e) => {
            if (e.key === "Enter") {
                doSearch();
            }
        }) as React.KeyboardEventHandler<HTMLInputElement>}></Input>
    </Segment>
};
const ProblemQuickAccessBox: React.FC<{}> = () => {
    const [text, setText] = useState("");
    const goto = useCallback(() => {
        if (text) {
            window.open(`/show_problem/${text}`);
        }
    }, [text]);
    return <Segment stacked>
        <Header as="h3">快速跳题</Header>
        <Input fluid action={<Button icon color="green" onClick={goto}>
            <Icon name="paper plane outline"></Icon>
        </Button>} placeholder="输入题号快速跳题..." value={text} onChange={(_, d) => setText(d.value)} onKeyDown={((e) => {
            if (e.key === "Enter") {
                goto();
            }
        }) as React.KeyboardEventHandler<HTMLInputElement>}></Input>
    </Segment>
};

export {
    BroadcastBox,
    ProblemtodoBox,
    FriendLinkBox,
    ToolBox,
    ProblemSearchBox,
    ProblemQuickAccessBox
}