import React, { useEffect, useState } from "react";
import { Button, Dimmer, Divider, Form, Header, List, Loader, Segment } from "semantic-ui-react";
import { Markdown } from "../../common/Markdown";
import { useDocumentTitle } from "../../common/Utils";
import { showSuccessModal } from "../../dialogs/Dialog";
import permissionPackClient from "./client/PermissionClient";
import { UserPermissionPackDetail } from "./client/types";

const UserPacks: React.FC<{}> = () => {
    useDocumentTitle("我的可用权限包");
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<UserPermissionPackDetail[]>([]);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setData(await permissionPackClient.getPermissionPacksForCurrentUser());
                    setLoaded(true);
                } catch { }
            })();
        }
    }, [loaded]);
    const claim = async (evt: React.MouseEvent<HTMLButtonElement>, id: number, index: number) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            await permissionPackClient.claimPermissionPack(id);
            const arr = [...data];
            arr[index].claimed = true;
            showSuccessModal("领取成功");
            setData(arr);
        } catch { }
        finally {
            target.classList.remove("loading");
        }
    };
    return <div>
        {!loaded && <Dimmer active>
            <Loader></Loader>
        </Dimmer>}
        <Header as="h1">
            可用权限包
        </Header>
        <Segment stacked>
            {data.map((x, i) => <>

                <Form key={i}>
                    <Header as="h3">
                        {x.name}
                    </Header>
                    {x.description !== null && x.description.trim() !== "" && <Form.Field>
                        <label>介绍</label>
                        <Segment>
                            <Markdown markdown={x.description}></Markdown>
                        </Segment>
                    </Form.Field>}
                    <Form.Field>
                        <label>权限列表</label>
                        <Segment>
                            <List>
                                {x.permissions.map((y, j) => <List.Item key={j}>
                                    {y}
                                </List.Item>)}
                            </List>
                        </Segment>
                    </Form.Field>
                    <Form.Field>
                        {x.claimed ? <div>
                            <div style={{ fontSize: "large", color: "red" }}>
                                您已领取过此权限包
                            </div>
                        </div> : <Button onClick={e => claim(e, x.id, i)} color="green">
                            领取
                        </Button>}
                    </Form.Field>

                </Form>
                <Divider></Divider>
            </>
            )}
        </Segment>
    </div>;
}

export default UserPacks;
