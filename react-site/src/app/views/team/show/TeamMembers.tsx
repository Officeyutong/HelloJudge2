import React, { useMemo } from "react";
import { Grid, Header, Segment, Popup, Button, Container, Label } from "semantic-ui-react";
import { useProfileImageMaker } from "../../../common/Utils";
import UserLink from "../../utils/UserLink";
import { TeamDetail } from "../client/types";

interface TeamMembersProps {
    members: TeamDetail["members"];
    admins: TeamDetail["admins"];
    owner_id: number;
    setAdmin: (uid: number, value: boolean) => void;
    kick: (uid: number) => void;
    hasManagePermission: boolean;
    isTeamOwner: boolean;
};
const UserCard: React.FC<{ data: TeamDetail["members"][0]; slot?: React.ReactNode }> = ({ data, slot }) => {
    const makeUrl = useProfileImageMaker();
    return <Segment style={{ wordBreak: "break-all" }}>
        <Grid columns="2">
            <Grid.Column width="4">
                <img alt="" src={makeUrl(data.email)} style={{ height: "38px", width: "38px", borderRadius: "19px" }}></img>
            </Grid.Column>
            <Grid.Column width="12">
                <Grid columns="1">
                    <Grid.Column style={{ fontSize: "20px" }}>
                        <UserLink data={data}></UserLink>
                    </Grid.Column>
                    <Grid.Column style={{ paddingTop: 0, paddingBottom: "5px" }}>
                        <Grid columns="2">
                            <Grid.Column >
                                <span style={{ color: "grey" }}>{data.group_name}</span>
                            </Grid.Column>
                            {slot && <Grid.Column>
                                {slot}
                            </Grid.Column>}
                        </Grid>
                    </Grid.Column>


                </Grid>
            </Grid.Column>
        </Grid>
    </Segment>;
}
const TeamMembers: React.FC<TeamMembersProps> = (props) => {
    const admins = useMemo(() => new Set(props.admins), [props.admins]);
    const normalMembers = useMemo(() => {
        const filtered = props.members.filter(x => (!admins.has(x.uid)) && x.uid !== props.owner_id);
        filtered.sort((x, y) => x.username < y.username ? -1 : 1);
        return filtered;
    }, [admins, props.members, props.owner_id]);
    const adminMembers = useMemo(() => props.members.filter(x => (admins.has(x.uid)) || x.uid === props.owner_id), [admins, props.members, props.owner_id])

    return <>
        <Header as="h3">
            管理员
        </Header>
        <Grid columns="3">
            {adminMembers.map(x => <Grid.Column key={x.uid}>
                <UserCard data={x} slot={x.uid !== props.owner_id ? (props.hasManagePermission && <Container textAlign="right">
                    <Popup
                        position="left center"
                        pinned
                        on="click"
                        trigger={<Button size="tiny" icon="add"></Button>}
                    >
                        <Button size="tiny" color="red" onClick={() => props.setAdmin(x.uid, false)}>取消管理</Button>
                    </Popup>
                </Container>) : <Label color="red">团队主</Label>}></UserCard>
            </Grid.Column>)}
        </Grid>
        {normalMembers.length !== 0 && <>
            <Header as="h3">
                普通用户
            </Header>
            <Grid columns="3">
                {normalMembers.map(x => <Grid.Column key={x.uid}>
                    <UserCard data={x} slot={props.hasManagePermission && <Container textAlign="right">
                        <Popup
                            position="left center"
                            pinned
                            on="click"
                            trigger={<Button size="tiny" icon="add"></Button>}
                        >
                            <Button.Group size="tiny">
                                <Button size="tiny" color="red" onClick={() => props.kick(x.uid)}>移出团队</Button>
                                {props.hasManagePermission && <Button size="tiny" color="green" onClick={() => props.setAdmin(x.uid, true)}>设为管理</Button>}
                            </Button.Group>

                        </Popup>
                    </Container>}></UserCard>
                </Grid.Column>)}
            </Grid>
        </>}
    </>;
};

export default TeamMembers;