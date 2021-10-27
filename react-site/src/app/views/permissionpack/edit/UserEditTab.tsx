import React, { useCallback, useEffect, useRef, useState } from "react";
import { Button, Dimmer, Divider, Form, Grid, Input, Loader, Pagination, Table } from "semantic-ui-react";
import { useInputValue } from "../../../common/Utils";
import { showConfirm } from "../../../dialogs/Dialog";
import { showSuccessPopup } from "../../../dialogs/Utils";
import permissionPackClient from "../client/PermissionClient";
import { PermissionPackUserItem } from "../client/types";

const UserEditTab: React.FC<{ id: number }> = ({ id }) => {
    const [data, setData] = useState<PermissionPackUserItem[]>([]);
    const [page, setPage] = useState(1);
    const [pageCount, setPageCount] = useState(0);
    const [loaded, setLoaded] = useState(false);
    const [loading, setLoading] = useState(false);
    const phoneColumn = useInputValue("1");
    const fileRef = useRef<HTMLInputElement>(null);
    const [uploading, setUploading] = useState(false);
    const [progressStr, setProgressStr] = useState("");
    const loadPage = useCallback((async (page: number) => {
        try {
            setLoading(true);
            let resp = await permissionPackClient.getPermissionPackUsers(id, page);
            setPageCount(resp.pageCount);
            setData(resp.data);
            setPage(page);
            setLoaded(true);
        } catch { } finally {
            setLoading(false);
        }
    }), [id]);
    useEffect(() => {
        if (!loaded) {
            loadPage(1);
        }
    }, [loaded, loadPage]);
    const remove = (phone: string) => {
        showConfirm("您确定要从权限包中删除该用户吗？如果您想要取消此用户使用相关题目、比赛、习题集的权限，请再在团队中删除此用户。", async () => {
            try {
                setLoading(true);
                await permissionPackClient.removePermissionPackUsers(id, [phone], false);
                await loadPage(page);
                showSuccessPopup("删除成功");
            } catch { } finally {
                setLoading(false);
            }
        })
    };
    const dropAll = () => showConfirm("您确定要删除所有记录吗?", async () => {
        try {
            setLoading(true);
            await permissionPackClient.removePermissionPackUsers(id, undefined, true);
            await loadPage(1);
            showSuccessPopup("删除成功");
        } catch { } finally {
            setLoading(false);
        }
    });
    const upload = async () => {
        const data = new FormData();
        data.append("file", fileRef.current!.files![0]);
        try {
            setUploading(true);
            await permissionPackClient.uploadUserList(id, parseInt(phoneColumn.value), data, (evt: any) => {
                setProgressStr(((evt.loaded / evt.total * 100) | 0) + "%");
            });
            await loadPage(1);
        } catch {

        } finally {
            setUploading(false);
        }
    };
    return <div>
        {loading && <Dimmer active>
            <Loader></Loader>
        </Dimmer>}
        <Form>
            <Form.Field>
                <label>上传xlsx文件</label>
                <input type="file" ref={fileRef} accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"></input>
            </Form.Field>
            <Form.Field>
                <label>表格中存储有手机号码数据的列</label>
                <Input {...phoneColumn}></Input>
            </Form.Field>
            <Button color="red" onClick={dropAll}>删除所有用户</Button>
            <Button color="green" loading={uploading} onClick={upload}>上传文件</Button>
            {uploading && <div>已上传 {progressStr}</div>}
        </Form>
        <Divider></Divider>
        <Grid columns="3" centered>
            <Grid.Column>
                <Pagination totalPages={pageCount} activePage={page} onPageChange={(e, d) => loadPage(d.activePage as number)}></Pagination>
            </Grid.Column>
        </Grid>
        <Table textAlign="center" celled>
            <Table.Header><Table.Row>
                <Table.HeaderCell>OJ用户名</Table.HeaderCell>
                <Table.HeaderCell>手机号码</Table.HeaderCell>
                <Table.HeaderCell>是否已领取权限</Table.HeaderCell>
                <Table.HeaderCell>操作</Table.HeaderCell>
            </Table.Row></Table.Header>
            <Table.Body>{data.map((x, i) => <Table.Row key={i}>
                <Table.Cell>{x.username}</Table.Cell>
                <Table.Cell>{x.phone}</Table.Cell>
                <Table.Cell positive={x.claimed} negative={!x.claimed}>
                    {x.claimed ? "是" : "否"}
                </Table.Cell>
                <Table.Cell>
                    <Button color="red" size="tiny" onClick={() => remove(x.phone)}>删除</Button>
                </Table.Cell>
            </Table.Row>)}</Table.Body>
        </Table>
    </div>;
};

export default UserEditTab;