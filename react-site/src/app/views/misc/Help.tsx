import { useEffect, useState } from "react";
import { Container, Dimmer, Header, Loader, Segment } from "semantic-ui-react";
import { Markdown } from "../../common/Markdown";
import { useDocumentTitle } from "../../common/Utils";
import miscClient from "./client/MiscClient";

const Help: React.FC<{}> = () => {
    const [loaded, setLoaded] = useState(false);
    const [text, setText] = useState("");
    useEffect(() => {
        if (!loaded) {
            miscClient.getHelpDoc().then(r => {
                setText(r);
                setLoaded(true);
            })
        }
    }, [loaded]);
    useDocumentTitle("帮助");
    return <>
        <Container textAlign="center">
            <Header as="h1">帮助</Header>
        </Container>
        <Segment stacked>
            {loaded && <Markdown markdown={text}></Markdown>}
            {!loaded && <>
                <div style={{ height: "400px" }}></div>
                <Dimmer active>
                    <Loader></Loader>
                </Dimmer>
            </>}
        </Segment>
    </>;
};

export default Help;