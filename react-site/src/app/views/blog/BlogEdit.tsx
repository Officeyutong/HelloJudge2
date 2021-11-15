import { DateTime } from "luxon";
import React, { useEffect, useRef, useState } from "react";
import { useHistory, useParams } from "react-router";
import { Button, Container, Dimmer, Form, Grid, Header, Loader, Segment } from "semantic-ui-react";
import { converter } from "../../common/Markdown";
import { useCurrentUid, useDocumentTitle } from "../../common/Utils";
import { useAceTheme } from "../../states/StateUtils";
import discussionClient from "../discussion/client/DiscussionClient";
import AceEditor from "react-ace";
import { PUBLIC_URL } from "../../App";
import { showSuccessModal } from "../../dialogs/Dialog";

const BlogEdit: React.FC<{}> = () => {
    const { id } = useParams<{ id?: string }>();
    const editing = id !== undefined;
    const numberId = id ? parseInt(id) : -1;
    const [title, setTitle] = useState("");
    const [content, setContent] = useState("");
    const [willPrivate, setPrivate] = useState(false);
    const [top, setTop] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [htmlContent, setHtmlContent] = useState("");
    const lastRender = useRef<number>(DateTime.now().toSeconds());
    const history = useHistory();
    useEffect(() => {
        if (!loaded) {
            if (editing) {
                (async () => {
                    try {
                        setLoading(true);
                        const resp = await discussionClient.getDiscussion(numberId);
                        setTitle(resp.title);
                        setContent(resp.content);
                        setHtmlContent(converter.makeHtml(resp.content));
                        setPrivate(resp.private);
                        setTop(resp.top);
                        setLoaded(true);

                    } catch { } finally {
                        setLoading(false);
                    }
                })();
            } else setLoaded(true);
        }
    }, [loaded, editing, numberId]);
    useDocumentTitle(`${editing ? "修改" : "发布"}博客`);
    useEffect(() => {
        if (DateTime.now().toSeconds() - lastRender.current >= 3) {
            setHtmlContent(converter.makeHtml(content));
            lastRender.current = DateTime.now().toSeconds();
        }
    }, [content]);
    const theme = useAceTheme();
    const uid = useCurrentUid();
    const submit = async () => {
        try {
            setLoading(true);
            if (editing) {
                await discussionClient.updateDiscussion(
                    numberId, content, title, top, willPrivate
                );
                showSuccessModal("更新成功!");
            } else {
                await discussionClient.postDiscussion(title, content, `blog.user.${uid}`, false, willPrivate);
                history.push(`${PUBLIC_URL}/blog/list/${uid}`);
            }
        } catch { } finally {
            setLoading(false);
        }
    };
    const remove = async () => {
        try {
            setLoading(true);
            await discussionClient.removeDiscussion(numberId);
            history.push(`${PUBLIC_URL}/blog/list/${uid}`);
        } catch { } finally { }
    };
    return <>
        {!loaded && loading && <>
            <div style={{ height: "400px" }}>
                <Dimmer active>
                    <Loader></Loader>
                </Dimmer>
            </div>
        </>}
        {loaded && <>
            <Header as="h1">
                {editing ? "修改博客" : "发布博客"}
            </Header>
            <Segment stacked>
                {loading && <Dimmer active>
                    <Loader></Loader>
                </Dimmer>}
                <Grid columns="2">
                    <Grid.Column width="8">
                        <Segment
                            style={{ overflowY: "scroll", wordWrap: "break-word", maxHeight: "800px" }}
                        >
                            <div dangerouslySetInnerHTML={{ __html: htmlContent }}></div>
                        </Segment>
                    </Grid.Column>
                    <Grid.Column width="8">
                        <Form>
                            <Form.Input label="标题" value={title} onChange={(_, d) => setTitle(d.value)}></Form.Input>
                            <Form.Checkbox toggle label="可见性" checked={willPrivate} onChange={(_, d) => setPrivate(d.checked!)}></Form.Checkbox>
                            <Form.Field>
                                <label>博客内容</label>
                                <AceEditor
                                    wrapEnabled
                                    width="100%"
                                    height="600px"
                                    value={content}
                                    onChange={setContent}
                                    theme={theme}
                                ></AceEditor>
                            </Form.Field>
                        </Form>
                        <Container textAlign="right">
                            <Button color="green" onClick={submit}>
                                提交
                            </Button>
                            {editing && <Button color="red" onClick={remove}>
                                删除
                            </Button>}
                        </Container>
                    </Grid.Column>
                </Grid>
            </Segment>
        </>}
    </>;
};

export default BlogEdit;