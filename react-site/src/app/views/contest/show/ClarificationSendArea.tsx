import React, { useState } from "react";
import { Button, Form, Grid, Header, Icon, Segment } from "semantic-ui-react";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-markdown";
import { useAceTheme } from "../../../states/StateUtils";
import { Markdown } from "../../../common/Markdown";
import { ButtonClickEvent } from "../../../common/types";
import contestClient from "../client/ContestClient";
interface ClarificationSendAreaProps {
    contest: number;
    refresh: () => void;
};

const ClarificationSendArea: React.FC<ClarificationSendAreaProps> = (props) => {
    const [content, setContent] = useState("");
    const theme = useAceTheme();
    const sendClar = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            await contestClient.sendClarification(props.contest, content);
            props.refresh();
        } catch { } finally {
            target.classList.remove("loading");
        }
    };
    return <>
        <Header as="h4">
            发送提问
        </Header>
        <Segment>
            <Form>
                <Form.Field>
                    <label>内容</label>
                    <AceEditor
                        value={content}
                        onChange={setContent}
                        theme={theme}
                        width="100%"
                        height="300px"
                        style={{ borderWidth: "1px" }}
                        mode="markdown"
                    ></AceEditor>
                </Form.Field>
                <Form.Field>
                    <label>预览</label>
                    <Markdown markdown={content}></Markdown>
                </Form.Field>
                <Grid columns="3" centered>
                    <Grid.Column>
                        <Button icon labelPosition="left" color="green" onClick={sendClar}>
                            <Icon name="paper plane"></Icon>
                            发送
                        </Button>
                    </Grid.Column>
                </Grid>
            </Form>

        </Segment>
    </>;
};

export default ClarificationSendArea;