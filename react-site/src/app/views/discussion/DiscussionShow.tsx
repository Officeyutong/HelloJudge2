import React, { useEffect, useState } from "react";
import { useParams } from "react-router";
import { Link } from "react-router-dom";
import { Dimmer, Grid, Header, Label, Loader, Image, Segment, Container, Divider, Form, Button } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { Markdown } from "../../common/Markdown";
import { ButtonClickEvent } from "../../common/types";
import { toLocalTime, useDocumentTitle, useProfileImageMaker } from "../../common/Utils";
import UserLink from "../utils/UserLink";
import discussionClient from "./client/DiscussionClient";
import { DiscussionDetail } from "./client/types";
import DiscussionComments from "./DiscussionComments";
import AceEditor from "react-ace";
import { useAceTheme } from "../../states/StateUtils";
const DiscussionShow: React.FC<{}> = () => {
    const { id } = useParams<{ id: string }>();
    const numberID = parseInt(id);
    const [loaded, setLoaded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<DiscussionDetail | null>(null);
    const [pathname, setPathname] = useState("");
    const [commentContent, setCommentContent] = useState("");
    // const [defaultCommentPage, setDefaultCommentPage] = useState(1);
    const theme = useAceTheme();
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setLoading(true);
                    const data = await discussionClient.getDiscussion(numberID);
                    setData(data);
                    setPathname(await discussionClient.getPathName(data.path));
                    setLoading(false);
                    setLoaded(true);
                } catch { } finally { }
            })();
        }
    }, [loaded, numberID]);
    useDocumentTitle(`${data?.title || "加载中..."} - 查看讨论`);
    const makeImg = useProfileImageMaker();
    const doReply = (username: string) => {
        setCommentContent(`@${username} `);
        window.scrollTo({ top: 99999 });
    };
    const sendComment = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            await discussionClient.postComment(commentContent, numberID);
            window.location.reload();
        } catch { } finally {
            target.classList.remove("loading");
        }
    };
    return <>
        {loading && <>
            <Segment stacked>
                <div style={{ height: "400px" }}></div>
                <Dimmer active>
                    <Loader></Loader>
                </Dimmer>
            </Segment>
        </>}
        {loaded && data !== null && <>
            <Header as="h2">
                {data.title}
            </Header>
            {data.private && <Label color="red">私有讨论</Label>}

            <Segment stacked>
                <Grid columns="2">
                    <Grid.Row>
                        <Grid.Column width="1">
                            <Image circular size="small" src={makeImg(data.email)}></Image>
                        </Grid.Column>
                        <Grid.Column width="15">
                            <div style={{ fontSize: "10px", color: "rgba(0,0,0,.6)", marginBottom: "10px" }}>
                                <UserLink data={{ uid: data.uid, username: data.username }}></UserLink>
                            </div>
                            <Container style={{ wordWrap: "break-word", wordBreak: "break-all" }}>
                                <Segment>
                                    <Markdown markdown={data.content}></Markdown>
                                </Segment>
                                <div style={{ fontSize: "10px", color: "rgba(0,0,0,.6)", top: "3px" }}>
                                    {toLocalTime(data.time)}
                                </div>

                            </Container>
                        </Grid.Column>
                    </Grid.Row>
                </Grid>

                <Divider></Divider>
                <div>
                    <Link to={`${PUBLIC_URL}/discussions/${data.path}/1`}>返回{pathname}</Link>
                </div>
                <Header as="h3">
                    评论
                </Header>
                <DiscussionComments
                    discussionID={numberID}
                    replyCallback={doReply}
                    defaultPage={1}
                ></DiscussionComments>
            </Segment>
            <Header as="h3">发表评论</Header>
            <Segment stacked>
                <Grid columns="2">
                    <Grid.Column>
                        <Form>
                            <Form.Field>
                                <AceEditor
                                    wrapEnabled
                                    value={commentContent}
                                    onChange={v => setCommentContent(v)}
                                    width="100%"
                                    height="300px"
                                    theme={theme}
                                ></AceEditor>
                            </Form.Field>
                            <Button color="green" onClick={sendComment}>
                                提交
                            </Button>
                        </Form>
                    </Grid.Column>
                    <Grid.Column>
                        <div style={{ overflowY: "scroll", maxHeight: "400px" }}>
                            <Markdown markdown={commentContent}></Markdown>
                        </div>
                    </Grid.Column>
                </Grid>

            </Segment>
        </>}
    </>;
};

export default DiscussionShow;