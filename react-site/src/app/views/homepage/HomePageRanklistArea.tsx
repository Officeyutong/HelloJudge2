import _ from "lodash";
import React, { useEffect, useState } from "react";
import { Dimmer, Header, Loader, Table } from "semantic-ui-react";
import { Markdown } from "../../common/Markdown";
import { GlobalRanklistItem } from "../user/client/types";
import userClient from "../user/client/UserClient";
import UserLink from "../utils/UserLink";

const HomepageRanklistArea: React.FC<{}> = () => {
    const [loaded, setLoaded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<GlobalRanklistItem[]>([]);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setLoading(true);
                    setData((await userClient.getGlobalRanklist(1)).ranklist);
                    setLoaded(true);
                } catch { } finally {
                    setLoading(false);
                }
            })();
        }
    }, [loaded]);
    return <>
        {loading && <>
            <div style={{ height: "200px" }}>
                <Dimmer active>
                    <Loader></Loader>
                </Dimmer>
            </div>
        </>}
        {loaded && <>
            <Header as="h2">
                排行榜
            </Header>
            <Table basic="very" celled>
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell textAlign="center">用户名</Table.HeaderCell>
                        <Table.HeaderCell textAlign="center">简介</Table.HeaderCell>
                        <Table.HeaderCell textAlign="center">Rating</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {_.take(data, 10).map((x, i) => <Table.Row key={i}>
                        <Table.Cell textAlign="center">
                            <UserLink data={{ uid: x.uid, username: x.username }}></UserLink>
                        </Table.Cell>
                        <Table.Cell textAlign="center">
                            <div style={{ maxHeight: "50px", overflowY: "hidden", overflowX: "hidden" }}>
                                <Markdown markdown={x.description}></Markdown>
                            </div>
                        </Table.Cell>
                        <Table.Cell textAlign="center">
                            {x.rating}
                        </Table.Cell>
                    </Table.Row>)}
                </Table.Body>
            </Table>
        </>}
    </>;
};


export default HomepageRanklistArea;