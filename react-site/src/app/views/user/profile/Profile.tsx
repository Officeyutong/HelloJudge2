import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { Card, Grid, Loader, Modal, Image, Button, Header, Segment, Table, Tab } from "semantic-ui-react";
import { PUBLIC_URL } from "../../../App";
import { useCurrentUid, useDocumentTitle, useProfileImageMaker } from "../../../common/Utils";
import { UserProfileResponse } from "../client/types";
import userClient from "../client/UserClient";
import AcceptedProblemsTab from "./AcceptedProblemsTab";
import DescriptionTab from "./DescriptionTab";
import GeneralFollowingTab from "./GeneralFollowingTab";
import JoinedTeamsTab from "./JoinedTeamsTab";

const Profile: React.FC<{}> = () => {
    const uid = parseInt(useParams<{ uid: string }>().uid);
    const [loading, setLoading] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<UserProfileResponse | null>(null);
    const [toggling, setToggling] = useState(false);
    const urlMaker = useProfileImageMaker();
    const currUser = useCurrentUid();
    useDocumentTitle(data === null ? "加载中" : `${data.username} - ${data.id} - 用户资料`);
    useEffect(() => {
        (async () => {
            if (!loaded) {
                try {
                    setLoading(true);
                    let resp = await userClient.getUserProfile(uid);
                    setLoaded(true);
                    setData(resp);
                } catch { } finally { setLoading(false); }
            }
        })();
    }, [loaded, uid]);
    const toggleFollowStateToThis = async () => {
        try {
            setToggling(true);
            let resp = await userClient.toggleFollowState(data!.id);
            setData({ ...data!, following: resp.followed });
        } catch { } finally {
            setToggling(false);
        }
    };
    return <div style={{ maxWidth: "1000px" }}>
        {loading && <Modal
            basic
            open={true}
        >
            <Modal.Content>
                <Loader></Loader>
            </Modal.Content>
        </Modal>}
        {data !== null && <Grid columns="2">
            <Grid.Column width="5">
                <Card>
                    <Image src={urlMaker(data.email, 200)}></Image>
                    <Card.Content>
                        <Card.Header>{data.username}</Card.Header>
                        <Card.Meta>
                            <span className="date">{data.register_time}</span>
                        </Card.Meta>
                        <Card.Meta>
                            <span>{data.group_name}</span>
                        </Card.Meta>
                    </Card.Content>
                    <Card.Content extra>
                        <div style={{ color: "black" }}>
                            <div>Rating: {data.rating}</div>
                            <div>Email: {data.email}</div>
                        </div>
                    </Card.Content>
                    {data.banned === 1 && <Card.Content extra>
                        <span style={{ color: "red" }}>此账户已被封禁</span>
                    </Card.Content>}
                    <Card.Content extra>
                        {(data.managable || currUser === data.id) && <Button size="tiny" as="a" target="_blank" href={`/profile_edit/${data.id}`}>设置</Button>}
                        <Button size="tiny" as={Link} to={`${PUBLIC_URL}/blog/list/${data.id}`}>博客</Button>
                        <Button loading={toggling} size="tiny" color={data.following ? "blue" : undefined} onClick={toggleFollowStateToThis}>{data.following ? "已关注" : "未关注"}</Button>
                    </Card.Content>
                </Card>
                <Header block attached="top" as="h4">
                    Rating历史
                </Header>
                <Segment attached="bottom">
                    <div style={{ overflowY: "scroll", maxHeight: "500px" }}>
                        {data.rating_history.length === 0 ? <div>这个人很懒，没参加如果任何Rated比赛...</div> : <Table basic="very" celled>
                            <Table.Header>
                                <Table.Row>
                                    <Table.HeaderCell>比赛</Table.HeaderCell>
                                    <Table.HeaderCell>变化</Table.HeaderCell>
                                </Table.Row>
                            </Table.Header>
                            <Table.Body>
                                {data.rating_history.map((x, i) => <Table.Row key={i}>
                                    <Table.Cell><a href={`/contest/${x.contest_id}`}>{x.contest_name}</a></Table.Cell>
                                    <Table.Cell>
                                        {x.result >= 0 ? <div style={{ color: "green" }}>+{x.result}</div> : <div style={{ color: "red" }}>-{-x.result}</div>}
                                    </Table.Cell>
                                </Table.Row>)}
                            </Table.Body>
                        </Table>}
                    </div>
                </Segment>
                {/* <Header block attached="top" as="h4">
                    通过题目
                </Header>
                <Segment attached="bottom" style={{ maxHeight: "500px", overflowY: "scroll" }}>
                    {data.ac_problems.length === 0 ? <div>这个人很懒，还没做过题</div> : <Grid style={{ marginRight: "5px" }} columns="6">
                        {data.ac_problems.map((x, i) => <Grid.Column key={i}>
                            <span>[<a href={`/show_problem/${x}`}>{x}</a>]</span>
                        </Grid.Column>)}
                    </Grid>}
                </Segment> */}
            </Grid.Column>
            <Grid.Column width="11">
                <Header as="h1">
                    {data.username}
                </Header>
                <Tab menu={{ attached: true }} renderActiveOnly={false} panes={[
                    { menuItem: "个人简介", pane: <Tab.Pane key={0}><DescriptionTab data={data.description}></DescriptionTab></Tab.Pane> },
                    { menuItem: "关注TA的人", pane: <Tab.Pane key={1}><GeneralFollowingTab provider={(page) => userClient.getFollowerList(data.id, page)}></GeneralFollowingTab></Tab.Pane> },
                    { menuItem: "TA关注的人", pane: <Tab.Pane key={2}><GeneralFollowingTab provider={(page) => userClient.getFolloweeList(data.id, page)}></GeneralFollowingTab></Tab.Pane> },
                    { menuItem: "TA加入的团队", pane: <Tab.Pane key={3}><JoinedTeamsTab data={data.joined_teams}></JoinedTeamsTab></Tab.Pane> },
                    { menuItem: "通过题目", pane: <Tab.Pane key={4}><AcceptedProblemsTab data={data.ac_problems}></AcceptedProblemsTab></Tab.Pane> },

                ]}></Tab>
            </Grid.Column>
        </Grid>}
    </div>;
};

export default Profile;