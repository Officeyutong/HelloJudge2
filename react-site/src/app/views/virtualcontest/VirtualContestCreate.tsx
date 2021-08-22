import { DateTime } from "luxon";
import { useEffect, useMemo, useState } from "react";
import { useHistory, useParams } from "react-router";
import { Button, Dimmer, Form, Header, Loader, Segment } from "semantic-ui-react";
import { secondsToString, useDocumentTitle } from "../../common/Utils";
import contestClient from "../contest/client/ContestClient";
import DateTimePicker from "react-datetime";
import "react-datetime/css/react-datetime.css";
import 'moment/locale/zh-cn';
import { ButtonClickEvent } from "../../common/types";
import virtualContestClient from "./client/VirtualcontestClient";
import { PUBLIC_URL } from "../../App";
function timeStampToString(seconds: number): string {
    return DateTime.fromSeconds(seconds).toJSDate().toLocaleString();
}

const VirtualContestCreate: React.FC<{}> = () => {
    const { id } = useParams<{ id: string }>();
    const numberID = parseInt(id);
    const [loaded, setLoaded] = useState(false);
    const [length, setLength] = useState(0);
    const [name, setName] = useState("");
    const timeString = useMemo(() => secondsToString(length), [length]);
    const [startTime, setStartTime] = useState<number>(Math.floor(DateTime.now().plus({ minute: 1 }).toSeconds()));
    const history = useHistory();
    const endTime = startTime + length;
    useDocumentTitle("创建虚拟比赛");
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    const resp = await contestClient.getContestDetail(numberID, -1);
                    setLength(resp.end_time - resp.start_time);
                    setName(resp.name);
                    setLoaded(true);
                } catch { } finally {

                }
            })();
        }
    }, [loaded, numberID]);
    const create = async (evt: ButtonClickEvent) => {
        const target = evt.currentTarget;
        try {
            target.classList.add("loading");
            const { id } = await virtualContestClient.createVirtualContest(numberID, startTime);
            history.push(`${PUBLIC_URL}/contest/${numberID}?virtual_contest=${id}`);
        } catch (e: any) {
            console.error(e);
        } finally {
            target.classList.remove("loading");
        }
    };
    return <>
        {!loaded && <div style={{ height: "400px" }}>
            <Dimmer active>
                <Loader></Loader>
            </Dimmer>
        </div>}
        {loaded && <>
            <Header as="h1">
                {name} 的虚拟比赛
            </Header>
            <Segment stacked style={{ maxWidth: "400px" }}>
                <Form>
                    <Form.Field>
                        <label>开始时间</label>
                        <DateTimePicker
                            value={DateTime.fromSeconds(startTime).toJSDate()}
                            onChange={v => {
                                if (typeof v === "string") return;
                                setStartTime(v.unix());
                            }}
                            locale="zh-cn"
                        ></DateTimePicker>
                    </Form.Field>
                    <Form.Field>
                        <label>持续时间</label>
                        <span>{timeString}</span>
                    </Form.Field>
                    <Form.Field>
                        <label>结束时间</label>
                        <span>{timeStampToString(endTime)}</span>
                    </Form.Field>
                    <Button color="green" onClick={create}>
                        创建
                    </Button>
                </Form>

            </Segment>
        </>}
    </>;
};

export default VirtualContestCreate;