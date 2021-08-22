import React, { useEffect, useState } from "react";
import { Dimmer, Form, Input, Loader } from "semantic-ui-react";
import permissionPackClient from "../client/PermissionClient";
import { PermissionPackDetail } from "../client/types";
import { useAceTheme } from "../../../states/StateUtils";
import AceEditor from "react-ace";
import { v4 as uuidv4 } from "uuid";
import { showSuccessModal } from "../../../dialogs/Dialog";
const InfoTab: React.FC<{ id: number; updateTitle: (s: string) => void; }> = ({ id, updateTitle }) => {
    const [data, setData] = useState<PermissionPackDetail | null>(null);
    const [permStr, setPermStr] = useState("");
    const [loaded, setLoaded] = useState(false);
    const theme = useAceTheme();
    const [loading, setLoading] = useState(false);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    let data = await permissionPackClient.getPermissionPackDetail(id);
                    setData(data);
                    setPermStr(data.permissions.join("\n"));
                    updateTitle(data.name);
                    setLoaded(true);
                } catch { }
            })();
        }
    }, [loaded, id, updateTitle]);
    const update = async () => {
        try {
            setLoading(true);
            await permissionPackClient.updatePermissionPackDetails(
                id,
                data!.name,
                data!.description,
                permStr.split("\n")
            );
        } catch { } finally {
            setLoading(false);
            showSuccessModal("更新完成");
        }
    };
    return <div>
        {(!loaded || loading) && <Dimmer active>
            <Loader></Loader></Dimmer>}
        {data !== null && <Form>
            <Form.Field>
                <label>名称</label>
                <Input value={data.name} onChange={(e, d) => {
                    updateTitle(d.value);
                    setData({ ...data, name: d.value });
                }}></Input>
            </Form.Field>
            <Form.Field>
                <label>介绍</label>
                <AceEditor
                    onChange={v => setData({ ...data, description: v })}
                    value={data.description}
                    name={uuidv4()}
                    theme={theme}
                    mode="markdown"
                    width="100%"
                    height="200px"
                ></AceEditor>
            </Form.Field>
            <Form.Field>
                <label>权限(一行一条)</label>
                <AceEditor
                    onChange={v => setPermStr(v)}
                    value={permStr}
                    name={uuidv4()}
                    theme={theme}
                    mode="plain_text"
                    width="100%"
                    height="200px"
                ></AceEditor>
            </Form.Field>
            <Form.Button color="green" onClick={update}>
                保存
            </Form.Button>
        </Form>}
    </div>
};

export default InfoTab;