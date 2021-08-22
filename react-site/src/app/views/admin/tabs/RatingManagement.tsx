import React, { useCallback, useEffect, useState } from "react";
import { Button, Dimmer, Divider, Icon, Input, Loader, Table } from "semantic-ui-react";
import { showConfirm } from "../../../dialogs/Dialog";
import { showSuccessPopup } from "../../../dialogs/Utils";
import { adminClient } from "../client/AdminClient";
import { RatedContestList } from "../client/types";

const RatingManagement: React.FC<{}> = () => {
    const [loading, setLoading] = useState(false);
    const [value, setValue] = useState("");
    const [contests, setContests] = useState<RatedContestList>([]);
    const [loaded, setLoaded] = useState(false);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                setLoading(true);
                setContests(await adminClient.getRatedContestList());
                setLoading(false);
                setLoaded(true);
            })();
        }
    }, [loaded]);
    const removeRatedContest = (id: number) => {
        showConfirm("进行此操作后，这场比赛以及在这场比赛之后的比赛都将会被取消Rated.", () => {
            (async () => {
                setLoading(true);
                try {
                    await adminClient.removeRatedContest(id);
                    setContests(await adminClient.getRatedContestList());
                    showSuccessPopup("操作完成");
                } catch (e) {
                    // throw e;
                } finally {
                    setLoading(false);
                }
            })();
        }, "您确定要取消一场比赛的Rated吗？");
    };
    const addRatedContest = useCallback(async () => {
        try {
            setLoading(true);
            await adminClient.addRatedContest(parseInt(value));
            setContests(await adminClient.getRatedContestList());
            showSuccessPopup("操作完成");
        } catch (e) {
            // throw e;
        } finally {
            setLoading(false);
        }
    }, [value]);
    return <div>
        <Dimmer active={loading}>
            <Loader>加载中</Loader>
        </Dimmer>
        <Input value={value} onChange={(e, d) => setValue(d.value)} placeholder="请输入比赛ID..."></Input>
        <Button onClick={addRatedContest}>应用Rating</Button>
        <Divider></Divider>
        <Table basic="very" celled>
            <Table.Header>
                <Table.Row>
                    <Table.HeaderCell>比赛名</Table.HeaderCell>
                    <Table.HeaderCell>参赛人数</Table.HeaderCell>
                    <Table.HeaderCell>Rated时间</Table.HeaderCell>
                    <Table.HeaderCell>操作</Table.HeaderCell>
                </Table.Row>
            </Table.Header>
            <Table.Body>
                {contests.map((x, i) => <Table.Row key={i}>
                    <Table.Cell>
                        <a rel="noreferrer" href={`/contest/${x.contestID}`} target="_blank">{x.contestName}</a>
                    </Table.Cell>
                    <Table.Cell>{x.contestantCount}</Table.Cell>
                    <Table.Cell>{x.ratedTime}</Table.Cell>
                    <Table.Cell><Button circular icon size="tiny" color="red" onClick={() => removeRatedContest(x.contestID)}>
                        <Icon name="times"></Icon></Button></Table.Cell>
                </Table.Row>)}
            </Table.Body>
        </Table>
    </div>;
};

export default RatingManagement;