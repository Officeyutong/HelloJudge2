import React, { useEffect, useState } from "react";
import { Button, Dimmer, Header, Loader, Table } from "semantic-ui-react";
import { showConfirm } from "../../dialogs/Dialog";
import { showSuccessPopup } from "../../dialogs/Utils";
import permissionPackClient from "./client/PermissionClient";
import { PermissionPackListItem } from "./client/types";

const PermissionPackList: React.FC<{}> = () => {
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<PermissionPackListItem[]>([]);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setData(await permissionPackClient.listPermissionPacks());
                    setLoaded(true);
                } catch { } finally { }
            })();
        }
    }, [loaded]);
    const create = async (evt: React.MouseEvent<HTMLButtonElement>) => {
        const list = evt.currentTarget.classList;
        try {
            list.add("loading");
            let resp = await permissionPackClient.createPermissionPack();
            setData([...data, { id: resp.id, name: resp.name, permissionCount: 0, userCount: 0 }]);
            window.scroll(0, 9999999);
            showSuccessPopup("添加成功");
        } catch { } finally {
            list.remove("loading");
        }
    }
    const remove = (evt: React.MouseEvent<HTMLButtonElement>, id: number) => {
        showConfirm("您确认要删除此权限包吗?", async () => {
            try {
                await permissionPackClient.removePermissionPack(id);
                let resp = data.filter(x => x.id !== id);
                setData(resp);
                showSuccessPopup("删除完成");
            } catch {

            } finally {

            }
        }, "询问");
    };
    return <div>
        {!loaded && <Dimmer active>
            <Loader></Loader>
        </Dimmer>}
        <Header as="h2">
            权限包管理
        </Header>
        <Button color="green" onClick={e => create(e)}>创建权限包</Button>
        <Table celled textAlign="center">
            <Table.Header><Table.Row>
                <Table.HeaderCell>权限包ID</Table.HeaderCell>
                <Table.HeaderCell>权限包名</Table.HeaderCell>
                <Table.HeaderCell>可使用用户数</Table.HeaderCell>
                <Table.HeaderCell>权限数</Table.HeaderCell>
                <Table.HeaderCell>操作</Table.HeaderCell>
            </Table.Row></Table.Header>
            <Table.Body>
                {data.map((x, i) => <Table.Row key={i}>
                    <Table.Cell>{x.id}</Table.Cell>
                    <Table.Cell>{x.name}</Table.Cell>
                    <Table.Cell>{x.userCount}</Table.Cell>
                    <Table.Cell>{x.permissionCount}</Table.Cell>
                    <Table.Cell>
                        <Button.Group size="tiny">
                            <Button size="tiny" color="red" onClick={e => remove(e, x.id)}>删除</Button>
                            <Button size="tiny" color="green" as="a" href={`/permissionpack/edit/${x.id}`} target="_blank">编辑</Button>
                        </Button.Group>
                    </Table.Cell>
                </Table.Row>)}
            </Table.Body>
        </Table>
    </div>;
}

export default PermissionPackList;
