import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { Button, Container, Dimmer, Divider, Grid, Header, Icon, Loader, Segment } from "semantic-ui-react";
import { useDocumentTitle } from "../../../common/Utils";
import contestClient from "../client/ContestClient";
import { ClarificationDetailResponse } from "../client/types";
import ClarificationArea from "./ClarificationArea";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-markdown";
import { useAceTheme } from "../../../states/StateUtils";
import { Markdown } from "../../../common/Markdown";
import { ButtonClickEvent } from "../../../common/types";
import { showSuccessModal } from "../../../dialogs/Dialog";

const ClarificationEdit: React.FC<{}> = () => {
    const { id } = useParams<{ id: string }>();
    const numberID = parseInt(id);
    useDocumentTitle("编辑提问回复");
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<ClarificationDetailResponse | null>(null);
    const [content, setContent] = useState("");
    const theme = useAceTheme();
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    const resp = await contestClient.getContestClarificationDetail(numberID);
                    setData(resp);
                    setLoaded(true);
                    if (resp.replied) setContent(resp.reply_content);
                } catch { } finally {
                }
            })();
        }
    }, [loaded, numberID]);
    const reply = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            await contestClient.replyClarification(numberID, content);
            showSuccessModal("回复完成");
        } catch { } finally {
            target.classList.remove("loading");
        }
    };
    return <>
        {!loaded && <div style={{ height: "400px" }}>
            <Dimmer active>
                <Loader></Loader>
            </Dimmer>
        </div>}
        {loaded && data !== null && <>
            <Header as="h1">
                比赛提问
            </Header>
            <Segment stacked>
                <ClarificationArea
                    {...data}
                    managable={true}
                    showEditReply={false}
                    removeCallback={() => { }}
                ></ClarificationArea>

            </Segment>
            <Header as="h3">
                编辑提问回复
            </Header>
            <Segment stacked>
                <Grid columns="2">
                    <Grid.Column>
                        <AceEditor
                            value={content}
                            onChange={setContent}
                            theme={theme}
                            mode="markdown"
                            width="100%"
                            height="400px"
                        ></AceEditor>
                    </Grid.Column>
                    <Grid.Column>
                        <Markdown markdown={content}></Markdown>
                    </Grid.Column>
                </Grid>
                <Divider vertical></Divider>
                <Container style={{ marginTop: "10px" }}>
                    <Button icon labelPosition="left" color="green" onClick={reply}>
                        <Icon name="paper plane"></Icon>
                        发送
                    </Button>
                </Container>
            </Segment>
        </>}
    </>;
};

export default ClarificationEdit;