import React from "react";
import {
    Container, Message, Segment, Header
} from "semantic-ui-react";
import { useDocumentTitle } from "../common/Utils";
const View404: React.FC<{}> = () => {
    useDocumentTitle("错误");
    return <Container>
        <Header as="h1">
            发生错误
        </Header>
        <Segment stacked style={{ fontSize: "large" }}>
            <Message error>
                <Message.Header>
                    错误
                </Message.Header>
                <Message.Content>
                    页面未找到
                </Message.Content>
            </Message>
        </Segment>

    </Container>;
};

export default View404;