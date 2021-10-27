import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Button, Container, Dimmer, Divider, Header, Icon, Loader, Segment, Table } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { ButtonClickEvent } from "../../common/types";
import { useDocumentTitle } from "../../common/Utils";
import UserLink from "../utils/UserLink";
import teamClient from "./client/TeamClient";
import { TeamListEntry } from "./client/types";

const TeamList: React.FC<{}> = () => {
    useDocumentTitle("团队列表");
    const [data, setData] = useState<TeamListEntry[]>([]);
    const [loaded, setLoaded] = useState(false);

    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    const resp = await teamClient.getTeamList();
                    setData(resp); setLoaded(true);
                } catch { } finally { }
            })();
        }
    }, [loaded]);
    const addTeam = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            const { team_id } = await teamClient.createTeam();
            window.open(`/team/${team_id}`);
            setData(await teamClient.getTeamList());
        } catch { } finally {
            target.classList.remove("loading");
        }
    };
    return <>
        <Header as="h1">
            团队列表
        </Header>
        {!loaded && <Segment stacked>
            <Dimmer active><Loader></Loader></Dimmer>
            <div style={{ height: "400px" }}></div></Segment>}
        {loaded && <Segment stacked>
            <Container textAlign="right">
                <Button color="green" labelPosition="left" icon onClick={addTeam}>
                    <Icon name="plus"></Icon>
                    添加团队...
                </Button>
            </Container>
            <Divider></Divider>
            <Table basic="very">
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell textAlign="center" style={{ maxWidth: "80px", width: "80px" }}>团队ID</Table.HeaderCell>
                        <Table.HeaderCell>团队名</Table.HeaderCell>
                        <Table.HeaderCell>创建者</Table.HeaderCell>
                        <Table.HeaderCell textAlign="center">访问权限</Table.HeaderCell>
                        <Table.HeaderCell textAlign="center">人数</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {data.map((x, i) => <Table.Row key={i}>
                        <Table.Cell textAlign="center" style={{ maxWidth: "80px", width: "80px" }}>{x.id}</Table.Cell>
                        <Table.Cell style={{ minWidth: "300px" }}>
                            {/* <a href={`/team/${x.id}`}>{x.name}</a> */}
                            <Link to={`${PUBLIC_URL}/team/${x.id}`}>{x.name}</Link>
                        </Table.Cell>
                        <Table.Cell>
                            <UserLink data={{ uid: x.owner_id, username: x.owner_username }}></UserLink>
                        </Table.Cell>
                        <Table.Cell textAlign="center" positive={x.accessible} negative={!x.accessible}>
                            {x.private ? <Icon name={x.accessible ? "lock open" : "lock"}></Icon> : "公开"}
                        </Table.Cell>
                        <Table.Cell textAlign="center">
                            {x.member_count}
                        </Table.Cell>
                    </Table.Row>)}
                </Table.Body>
            </Table>
        </Segment>}
    </>;
};

export default TeamList;