import JSZip from "jszip";
import _ from "lodash";
import QueryString from "qs";
import React, { useEffect, useMemo, useRef, useState } from "react";
import { useLocation, useParams } from "react-router";
import { Dimmer, Form, Header, List, Loader, Message, Progress, Segment } from "semantic-ui-react";
import { ButtonClickEvent } from "../../common/types";
import { useDocumentTitle } from "../../common/Utils";
import { showErrorModal } from "../../dialogs/Dialog";
import contestClient from "../contest/client/ContestClient";
import { ContestProblemShow } from "../contest/client/types";
import problemClient from "../problem/client/ProblemClient";
import { ProblemInfo } from "../problem/client/types";

const SubmitAnswer: React.FC<{}> = () => {
    const location = useLocation();
    const { virtualID, contest } = QueryString.parse(location.search.substr(1)) as { virtualID?: string; contest?: string };
    const { problem } = useParams<{ problem: string }>();
    const [loaded, setLoaded] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [data, setData] = useState<ContestProblemShow | ProblemInfo | null>(null);
    const [progress, setProgress] = useState(0);
    const usingContest = contest !== undefined;
    const inputRef = useRef<HTMLInputElement>(null);
    const allCases = useMemo(() => data === null ? [] : _.sortBy(_.concat([], ...data.subtasks.map(x => x.testcases.map(y => y.output)))), [data]);
    useDocumentTitle(`${data?.title || "加载中..."} - 提交答案`);
    useEffect(() => {
        if (!loaded) {
            //夹带私货(x)
            const MnFe = {
                love: (target: string) => console.log(`MnFe ♥ ${target}`)
            };
            const Pb = "Pb";
            MnFe.love(Pb);
            (async () => {
                try {
                    if (usingContest) {
                        const resp = await contestClient.getContestProblemDetail(parseInt(problem), parseInt(contest || "-1"), parseInt(virtualID || "-1"));
                        setData(resp);
                    } else {
                        const resp = await problemClient.getProblemInfo(parseInt(problem), false);
                        setData(resp);
                    }
                    setLoaded(true);
                } catch { }
            })();
        }
    }, [contest, loaded, problem, usingContest, virtualID]);
    const submit = async (evt: ButtonClickEvent) => {
        if (!inputRef.current) return;
        const element = inputRef.current;
        if (!element.files) {
            showErrorModal("请选择文件");
            return;
        }
        if (element.files.length !== 1) {
            showErrorModal("请选择恰好一个文件!");
            return;
        }
        const inst = new JSZip();
        try {
            setSubmitting(true);
            const userFile = await inst.loadAsync(element.files[0]);
            const userNames = new Set(Object.keys(userFile.files));
            const missingFiles = allCases.filter(x => !userNames.has(x));
            if (missingFiles.length !== 0) {
                showErrorModal(`您的压缩包中缺少以下文件: ${missingFiles.join(",")}`);
                return;
            }
            const resp = await problemClient.submitWithAnswer(element.files[0], problem, parseInt(contest || "-1"), parseInt(virtualID || "-1"), evt => {
                setProgress(Math.floor(evt.loaded / evt.total * 100));
            });
            window.location.href = `/show_submission/${resp}`;
        } catch { } finally {
            setSubmitting(false);
        }

    };
    return <>
        <Header as="h1">
            提交答案 {loaded && data !== null && `- #${data.id}. ${data.title}`}
        </Header>
        <Segment style={{ maxWidth: "70%" }}>
            {!loaded && <>
                <div style={{ height: "400px" }}></div>
                <Dimmer active> <Loader></Loader></Dimmer>
            </>}
            {loaded && data !== null && <>
                <Message info>
                    <Message.Header>
                        请确保您的zip压缩包内有以下文件:
                    </Message.Header>
                    <Message.Content>
                        <List>
                            {allCases.map((x, i) => <List.Item key={i}>{x}</List.Item>)}
                        </List>
                    </Message.Content>
                </Message>
            </>}
            {submitting && <Progress percent={progress} progress="percent" active color="green"></Progress>}
            <Form>
                <Form.Field>
                    <label>压缩包</label>
                    <input type="file" ref={inputRef} accept="application/zip"></input>
                </Form.Field>
                <Form.Button onClick={submit} color="green" >
                    提交
                </Form.Button>
            </Form>
        </Segment>
    </>;
};

export default SubmitAnswer;