import React, { useEffect, useState } from "react";
import { Button, Dimmer, Grid, Loader, Modal } from "semantic-ui-react";
import userClient from "../client/UserClient";

const ShowAllPermissions: React.FC<{ onClose: () => void; uid: number; }> = ({ onClose, uid }) => {
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<string[]>([]);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setData(await userClient.getAllPermissions(uid));
                    setLoaded(true);
                } catch { } finally { }
            })();
        }
    }, [loaded, uid]);
    return <div>
        <Modal size="large" open={true}>
            <Modal.Header>所有权限</Modal.Header>
            <Modal.Content>
                {!loaded && <Dimmer active><Loader></Loader></Dimmer>}
                <Grid columns="8">
                    {data.map((x, i) => <Grid.Column key={i}>
                        <div style={{ wordBreak: "break-word" }}>{x}</div>
                    </Grid.Column>)}
                </Grid>
            </Modal.Content>
            <Modal.Actions>
                <Button onClick={onClose}>
                    关闭
                </Button>
            </Modal.Actions>
        </Modal>
    </div>;
};


export default ShowAllPermissions;