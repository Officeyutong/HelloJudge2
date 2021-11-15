import React, { useReducer, useState } from "react";
import { Link } from "react-router-dom";
import { Button, Card, Dimmer, Divider, Form, Grid, Header, Icon, Label, Loader, Segment } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { Markdown } from "../../common/Markdown";
import { ButtonClickEvent } from "../../common/types";
import { useDocumentTitle } from "../../common/Utils";
import challengeClient from "./client/ChallengeClient";
import { ChallengeDetail, ChallengeListEntry } from "./client/types";

interface ChallengeEntryProps extends ChallengeListEntry {
    managable: boolean;
};
interface ChallengeEntryReducerType {
    data: ChallengeDetail;
    loaded: boolean;
}
type Actions = { type: "update"; payload: ChallengeDetail } | { type: "reset" }
const ChallengeEntry: React.FC<ChallengeEntryProps> = (props) => {
    const [state, dispatch] = useReducer((state: ChallengeEntryReducerType, action: Actions) => {
        switch (action.type) {
            case "reset":
                return ({ data: state.data, loaded: false });
            case "update":
                return ({
                    data: action.payload,
                    loaded: true
                });
            default:
                return state;
        }

    }, {
        data: { ...props, problemsetList: props.problemsetList.map(t => ({ name: "", id: t, hasFinished: false })) },
        loaded: false
    });
    useDocumentTitle("天梯");
    const data = state.data;
    const managable = props.managable;
    // const locked = !data.accessible;
    const [reloading, setReloading] = useState(false);

    const loadDetails = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            const resp = await challengeClient.getChallengeDetail(data.id);
            dispatch({ payload: resp, type: "update" });
        } catch { } finally {
            target.classList.remove("loading");
        }
    };
    const unlock = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            await challengeClient.unlockChallenge(data.id);
            const resp = await challengeClient.getChallengeDetail(data.id);
            dispatch({ payload: resp, type: "update" });
        } catch { } finally {
            target.classList.remove("loading");
        }
    };
    const finishProblemset = async (id: number) => {
        try {
            setReloading(true);
            await challengeClient.finishProblemset(data.id, id);
            dispatch({ type: "update", payload: await challengeClient.getChallengeDetail(data.id) });
        } catch { } finally {
            setReloading(false);
        }
    };
    return <>
        <Header as="h2">
            {data.name}
        </Header>
        <Segment>
            {reloading && <Dimmer active>
                <Loader></Loader>
            </Dimmer>}
            <Form widths="equal">
                <Form.Group widths="equal">
                    <Form.Field>
                        <label>挑战等级</label>
                        <span>{data.level}</span>
                    </Form.Field>
                    <Form.Field>
                        <label>完成状态</label>
                        {data.hasFinished && <span style={{ color: "green" }}>已完成</span>}
                        {!data.hasFinished && <span style={{ color: "red" }}>未完成</span>}
                    </Form.Field>
                    <Form.Field>
                        <label>习题集数量</label>
                        <span>{data.problemsetList.length}</span>
                    </Form.Field>
                </Form.Group>

            </Form>
            {data.description !== "" && <>
                <Header as="h3">
                    说明
                </Header>
                <Markdown markdown={data.description}></Markdown>
            </>}
            <Divider></Divider>
            {data.problemsetList.length !== 0 && state.loaded && <>
                <Grid columns="4">
                    {data.problemsetList.map((item, i) => <Grid.Column key={i}>
                        <Card>
                            <Card.Content>
                                <Card.Header>
                                    <Link to={`${PUBLIC_URL}/problemset/show/${item.id}`}>
                                        {item.name}
                                    </Link>
                                </Card.Header>
                            </Card.Content>
                            <Card.Content extra>
                                {item.hasFinished && <Label color="green">
                                    <Icon name="checkmark"></Icon>
                                    习题集已完成</Label>}
                                {!item.hasFinished && <Button onClick={() => finishProblemset(item.id)} color="green" size="small">
                                    检查完成情况
                                </Button>}
                            </Card.Content>
                        </Card>
                    </Grid.Column>)}
                </Grid>
                <Divider></Divider>
            </>}
            {!data.accessible && <Button color="green" onClick={unlock}>
                解锁</Button>}
            {data.accessible && <Button color="green" onClick={loadDetails}>
                {state.loaded ? "刷新" : "展开"}
            </Button>}
            {managable && <Button color="blue" as={Link} to={`${PUBLIC_URL}/challenge/edit/${data.id}`}>编辑</Button>}
        </Segment>
    </>;
};

export default ChallengeEntry;