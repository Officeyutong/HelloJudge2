import { Container, Grid, Image, Segment } from "semantic-ui-react";
import { Markdown } from "../../../common/Markdown";
import { useProfileImageMaker } from "../../../common/Utils";
import UserLink from "../../utils/UserLink";
import { ClarificationDetailResponse } from "../client/types";

interface ClarificationAreaProps extends ClarificationDetailResponse {
    showEditReply: boolean;
    managable: boolean;
    removeCallback: () => void;
};

const ClarificationArea: React.FC<ClarificationAreaProps> = (props) => {
    const managable = props.managable;
    const makeProfileImage = useProfileImageMaker();
    return <Grid columns="2">
        <Grid.Row>
            <Grid.Column style={{ width: "65px" }}>
                <Image size="small" circular src={makeProfileImage(props.sender.email)}></Image>
            </Grid.Column>
            <Grid.Column style={{ maxWidth: "1000px", width: "90%" }}>
                <div style={{ fontSize: "10px", color: "rgba(0, 0, 0, 0.6)", marginBottom: "10px" }}>
                    <UserLink data={props.sender}></UserLink>
                </div>
                <Container style={{ overflowWrap: "break-word", wordBreak: "break-all" }}>
                    <div style={{ maxHeight: "400px", overflowY: "scroll" }}>
                        <Segment>
                            <Markdown markdown={props.content}></Markdown>
                        </Segment>
                    </div>
                    <div style={{ fontSize: "10px", color: "rgba(0, 0, 0, 0.6)", top: "3px" }}>
                        <Grid columns="2">
                            <Grid.Column>
                                <Container textAlign="left">
                                    {props.send_time}
                                </Container>
                            </Grid.Column>
                            <Grid.Column>
                                <Container textAlign="right">
                                    {managable && props.showEditReply && <a target="_blank" rel="noreferrer" href={`/contest/clarification/edit/${props.id}`}>编辑回复</a>}
                                    |
                                    {// eslint-disable-next-line jsx-a11y/anchor-is-valid
                                        managable && props.showEditReply && <a style={{ cursor: "pointer" }} onClick={props.removeCallback}>删除本条</a>
                                    }
                                </Container>
                            </Grid.Column>
                        </Grid>
                    </div>
                </Container>
                {props.replied && <Grid columns="2">
                    <Grid.Column style={{ width: "65px" }}>
                        <Image size="small" circular src={makeProfileImage(props.replier.email)}></Image>
                    </Grid.Column>
                    <Grid.Column style={{ width: "90%" }}>
                        <div style={{ fontSize: "10px", color: "rgba(0, 0, 0, 0.6)", marginBottom: "10px" }}>
                            <UserLink data={props.replier}></UserLink>
                        </div>
                        <Container style={{ overflowWrap: "break-word", wordBreak: "break-all" }}>
                            <div style={{ maxHeight: "400px", overflowY: "scroll" }}>
                                <Segment>
                                    <Markdown markdown={props.reply_content}></Markdown>
                                </Segment>
                            </div>
                            <div style={{ fontSize: "10px", color: "rgba(0, 0, 0, 0.6)", top: "3px" }}>
                                <Container textAlign="left">
                                    {props.reply_time}
                                </Container>
                            </div>
                        </Container>
                    </Grid.Column>
                </Grid>}
            </Grid.Column>
        </Grid.Row>
    </Grid>;
};

export default ClarificationArea;
