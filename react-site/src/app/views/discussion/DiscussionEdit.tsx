import React, { useEffect, useState } from "react";
import { Button, Checkbox, Dimmer, Form, Grid, Input, Loader, Segment } from "semantic-ui-react";
import AceEditor from "react-ace";
import { useAceTheme } from "../../states/StateUtils";
import discussionClient from "./client/DiscussionClient";
import axios, { Canceler } from "axios";
import { Markdown } from "../../common/Markdown";
import { ButtonClickEvent } from "../../common/types";
interface DiscussionEditProps {
    id: number;
    edit: boolean;
    finishCallback: () => void;
    path: string;
};

const DiscussionEdit: React.FC<DiscussionEditProps> = ({ id, edit, finishCallback, path }) => {
    const theme = useAceTheme();
    const [title, setTitle] = useState("");
    const [content, setContent] = useState("");
    const [top, setTop] = useState(false);
    const [loading, setLoading] = useState(false);
    const save = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            if (edit) {
                await discussionClient.updateDiscussion(id, content, title, top);
            } else {
                await discussionClient.postDiscussion(title, content, path, top);
            }
            finishCallback();
        } catch { } finally {
            target.classList.remove("loading");
        }
    };
    useEffect(() => {
        if (edit) {
            let canceler: Canceler | null = null;
            let done: boolean = false;
            setLoading(true);
            discussionClient.getDiscussion(id, new axios.CancelToken(c => { canceler = c })).then(resp => {
                done = true;
                setTitle(resp.title);
                setContent(resp.content);
                setTop(resp.top);
                setLoading(false);
            });
            return () => { if (!done && canceler) canceler(); setLoading(false); };
        }
    }, [id, edit]);
    return <>
        {loading && <>
            <div style={{ height: "400px" }}>
                <Dimmer active> <Loader></Loader></Dimmer>
            </div>
        </>}
        <Segment stacked>
            <Grid columns="2">
                <Grid.Row>
                    <Grid.Column>
                        <Form>
                            <Form.Field>
                                <label>标题</label>
                                <Input value={title} onChange={(_, d) => setTitle(d.value)}></Input>
                            </Form.Field>
                            <Form.Field>
                                <label>内容</label>
                                <AceEditor
                                    wrapEnabled
                                    value={content}
                                    onChange={v => setContent(v)}
                                    width="100%"
                                    height="300px"
                                    theme={theme}
                                ></AceEditor>
                            </Form.Field>
                            <Form.Field>
                                <Checkbox toggle checked={top} label="置顶" onChange={(_, d) => setTop(d.checked!)}></Checkbox>
                            </Form.Field>
                            <Form.Field>
                                <Button onClick={save} color="green">
                                    {edit ? "更新" : "发送"}
                                </Button>
                            </Form.Field>
                        </Form>
                    </Grid.Column>
                    <Grid.Column>
                        <div style={{ overflowY: "scroll", maxHeight: "400px"}}>
                            <Markdown markdown={content}></Markdown>
                        </div>
                    </Grid.Column>
                </Grid.Row>
            </Grid>
        </Segment>
    </>;
}

export default DiscussionEdit;