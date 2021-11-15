import QueryString from "qs";
import { useLocation } from "react-router";
import { Container, Header, Message, Segment } from "semantic-ui-react";
import { useDocumentTitle } from "../common/Utils";

interface ErrorAndSuccessProps {
    error: boolean;
};

const ErrorAndSuccess: React.FC<ErrorAndSuccessProps> = ({ error }) => {
    const location = useLocation();
    let parsed: { message?: string; title?: string; } = QueryString.parse(location.search.substr(1));
    useDocumentTitle(error ? "错误" : "操作完成");

    return error ? <Container>
        <Header as="h1">发生错误</Header>
        <Segment stacked style={{ fontSize: "large" }}>
            <Message error>
                <Message.Header>{parsed.title || "错误"}</Message.Header>
                <Message.Content>
                    <p>{parsed.message}</p>
                </Message.Content>
            </Message>
        </Segment>
    </Container> : <Container>
        <Segment stacked>
            <Message success>
                <Message.Header>{parsed.title || "成功"}</Message.Header>
                <Message.Content>
                    <p>{parsed.message}</p>
                </Message.Content>
            </Message>
        </Segment>

    </Container>;
}

export default ErrorAndSuccess;