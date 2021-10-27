import React, { useCallback, useEffect, useState } from "react";
import { Button, Dimmer, Divider, Form, Header, Input, Loader } from "semantic-ui-react";
import { PermissionGroupInstance, PermissionGroupList } from "../client/types";
import AceEditor from "react-ace";
import { v4 as uuidv4 } from "uuid";
import { adminClient } from "../client/AdminClient";
import _ from "lodash";
import { showSuccessPopup } from "../../../dialogs/Utils";
import "ace-builds/src-noconflict/mode-plain_text";
import "ace-builds/src-noconflict/theme-github";
import { useAceTheme } from "../../../states/StateUtils";
const PermissionGroupItemEdit: React.FC<{
    data: PermissionGroupInstance;
    onUpdate: (d: PermissionGroupInstance) => void;
}> = ({ data, onUpdate }) => {
    // const [theme, themeURL] = useAceThemeTuple();
    const theme = useAceTheme();
    return <div>
        <Header as="h3">{data.name}</Header>
        <Form>
            <Form.Field>
                <label>权限组ID</label>
                <Input value={data.id} onChange={(_, d) => onUpdate(({ ...data, id: d.value }))}></Input>
            </Form.Field>
            <Form.Field>
                <label>权限组名</label>
                <Input value={data.name} onChange={(_, d) => onUpdate({ ...data, name: d.value })}></Input>
            </Form.Field>
            <Form.Field>
                <label>继承自</label>
                <Input value={data.inherit} onChange={(_, d) => onUpdate({ ...data, inherit: d.value })}></Input>
            </Form.Field>
            <Form.Field>
                <label>权限列表(以换行分隔)</label>
                <AceEditor
                    onChange={v => onUpdate({ ...data, permissions: v })}
                    value={data.permissions}
                    name={uuidv4()}
                    theme={theme}
                    mode="plain_text"
                ></AceEditor>
            </Form.Field>

        </Form>
    </div>;
};

const PermissionGroupTab: React.FC<{}> = () => {
    const [loading, setLoading] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<PermissionGroupList | null>(null);

    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setLoading(true);
                    setData(await adminClient.getPermissionGroupList());
                    setLoaded(true);
                } catch (e) {

                } finally { setLoading(false) }
            })();
        }
    }, [loaded]);
    const save = useCallback(async () => {
        try {
            setLoading(true);
            await adminClient.updatePermissionGroupList(data!);
            showSuccessPopup("更新完成!");
        } catch (e) { } finally { setLoading(false); }
    }, [data]);
    return <div>
        {loading && <div style={{ height: "400px" }}>
            <Dimmer active>
                <Loader>加载中...</Loader>
            </Dimmer>
        </div>}
        {loaded && <div>
            {data!.map((item, i) => <div key={i}>
                <PermissionGroupItemEdit
                    data={item}
                    onUpdate={e => {
                        const d = [...data!];
                        d[i] = e;
                        setData(d);
                    }}
                ></PermissionGroupItemEdit>
                <Button color="red" onClick={() => setData(_.slice(data, i, i + 1))}>删除</Button>
                <Divider></Divider>
            </div>)}
            <Button color="green" onClick={() => setData([...data!, { id: "ID", name: "新权限组", inherit: "default", permissions: "" }])}>添加</Button>
            <Button color="green" onClick={save}>保存</Button>
        </div>}
    </div>;
};

export default PermissionGroupTab;