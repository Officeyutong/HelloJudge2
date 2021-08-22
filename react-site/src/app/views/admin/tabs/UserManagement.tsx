import React, { useCallback, useState } from "react";
import { Button, Header, Input } from "semantic-ui-react";
import { adminClient } from "../client/AdminClient";

const UserManagement: React.FC<{}> = () => {
    const [uid, setUid] = useState("-1");
    const [switchLoading, setSwitchLoading] = useState(false);
    const switchUser = useCallback(async () => {
        try {
            setSwitchLoading(true);
            await adminClient.switchUser(parseInt(uid));
            window.location.href = "/";
        } catch (e) { } finally { setSwitchLoading(false); }
    }, [uid]);
    return <div>
        <Header as="h3">
            切换用户
        </Header>
        <Input value={uid} onChange={(_, d) => setUid(d.value)} action={<Button onClick={switchUser} loading={switchLoading} color="green">切换</Button>}>

        </Input>
    </div>;
}

export default UserManagement;
