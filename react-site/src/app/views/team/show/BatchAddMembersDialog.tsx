import { useMemo, useState } from "react";
import { Button, Checkbox, Dimmer, Grid, Input, Loader, Modal, Table } from "semantic-ui-react";
import { KeyDownEvent } from "../../../common/types";
import { useInputValue } from "../../../common/Utils";
import { GlobalRanklistItem } from "../../user/client/types";
import userClient from "../../user/client/UserClient";
import UserLink from "../../utils/UserLink";
import teamClient from "../client/TeamClient";
import { TeamDetail } from "../client/types";

interface BatchAddMembersProps {
    team: number;
    finishCallback: () => void;
    onClose: () => void;
    open: boolean;
    teamMembers: TeamDetail["members"];
};

const BatchAddMembers: React.FC<BatchAddMembersProps> = ({ team, finishCallback, onClose, open, teamMembers }) => {
    const [used, setUsed] = useState<GlobalRanklistItem[]>([]);
    const [searchResult, setSearchResult] = useState<GlobalRanklistItem[]>([]);
    const searchText = useInputValue();
    const [searching, setSearching] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [beAdmin, setBeAdmin] = useState(false);
    const usedSet = useMemo(() => new Set(used.map(x => x.uid)), [used]);
    const memberSet = useMemo(() => new Set(teamMembers.map(x => x.uid)), [teamMembers]);
    const doSearch = async () => {
        try {
            setSearching(true);
            const resp = await userClient.getGlobalRanklist(1, searchText.value);
            setSearchResult(resp.ranklist);
        } catch { } finally {
            setSearching(false);
        }
    };
    const submit = async () => {
        try {
            setSubmitting(true);
            await teamClient.batchAddMembers(team, used.map(x => x.uid), beAdmin);
            finishCallback();
            onClose();
        } catch { } finally {
            setSubmitting(false);
        }
    };
    return <Modal
        open={open}
        onClose={onClose}
        closeOnDimmerClick={false}
    >
        <Modal.Header>
            批量添加用户
        </Modal.Header>
        <Modal.Content>
            {submitting && <Dimmer active>
                <Loader></Loader>
            </Dimmer>}
            <Grid columns="2">
                <Grid.Column>
                    {searching && <Dimmer active>
                        <Loader></Loader>
                    </Dimmer>}
                    <Grid columns="1">
                        <Grid.Column>
                            <Input {...searchText} placeholder="输入用户名进行搜索" fluid actionPosition="left" action={{
                                color: "green",
                                content: "搜索",
                                onClick: doSearch
                            }} onKeyDown={(evt: KeyDownEvent) => {
                                if (evt.code === "Enter") {
                                    doSearch();
                                }
                            }}></Input>
                        </Grid.Column>
                        <Grid.Column style={{ overflowY: "scroll", maxHeight: "400px" }}>
                            <Table>
                                <Table.Header>
                                    <Table.Row>
                                        <Table.HeaderCell>UID</Table.HeaderCell>
                                        <Table.HeaderCell>用户名</Table.HeaderCell>
                                        <Table.HeaderCell>操作</Table.HeaderCell>
                                    </Table.Row>
                                </Table.Header>
                                <Table.Body>
                                    {searchResult.map(x => <Table.Row key={x.uid}>
                                        <Table.Cell>{x.uid}</Table.Cell>
                                        <Table.Cell><UserLink data={x}></UserLink></Table.Cell>
                                        <Table.Cell>
                                            <Button color="green" size="tiny" onClick={() => setUsed([...used, x])} disabled={usedSet.has(x.uid) || memberSet.has(x.uid)}>添加</Button>
                                        </Table.Cell>
                                    </Table.Row>)}
                                    {searchResult.length === 0 && <Table.Cell colSpan={2}>
                                        搜索无结果...
                                    </Table.Cell>}
                                </Table.Body>
                            </Table>
                        </Grid.Column>
                    </Grid>
                </Grid.Column>
                <Grid.Column style={{ overflowY: "scroll", maxHeight: "400px" }}>
                    <Checkbox toggle checked={beAdmin} onChange={(e, d) => setBeAdmin(d.checked!)} label="设置为团队管理员"></Checkbox>
                    <Table>
                        <Table.Header>
                            <Table.Row>
                                <Table.HeaderCell>用户</Table.HeaderCell>
                                <Table.HeaderCell>操作</Table.HeaderCell>
                            </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {used.map(x => <Table.Row key={x.uid}>
                                <Table.Cell><UserLink data={x}></UserLink></Table.Cell>
                                <Table.Cell><Button size="tiny" color="red" onClick={() => setUsed(used.filter(y => y.uid !== x.uid))}>移除</Button></Table.Cell>
                            </Table.Row>)}
                        </Table.Body>
                    </Table>
                </Grid.Column>
            </Grid>
        </Modal.Content>
        <Modal.Actions>
            <Button onClick={submit} color="green">
                确定
            </Button>
            <Button onClick={onClose} color="red">
                取消
            </Button>
        </Modal.Actions>
    </Modal>;
};

export default BatchAddMembers;