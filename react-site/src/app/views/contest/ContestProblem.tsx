import QueryString from "qs";
import React, { useEffect, useRef, useState } from "react";
import { useLocation, useParams } from "react-router";
import { Button, Dimmer, Grid, Header, Icon, Loader, Rail, Ref, Segment, Sticky, Table } from "semantic-ui-react";
import { ProgrammingLanguageEntry } from "../../common/types";
import { useDocumentTitle } from "../../common/Utils";
import { showConfirm } from "../../dialogs/Dialog";
import problemClient from "../problem/client/ProblemClient";
import CodeInput from "../problem/CodeInput";
import FileDownloadArea from "../problem/FileDownloadArea";
import ProblemStatementView from "../problem/ProblemStatementView";
import utilClient from "../utils/client/UtilClient";
import contestClient from "./client/ContestClient";
import { ContestProblemShow } from "./client/types";

const ContestProblem: React.FC<{}> = () => {
    const { contestID, problemID } = useParams<{ contestID: string; problemID: string }>();
    const location = useLocation();
    const virtualID = parseInt(QueryString.parse(location.search.substr(1)).virtual_contest as string || "-1");
    const numberContestID = parseInt(contestID);
    const [data, setData] = useState<ContestProblemShow | null>(null);
    const [loaded, setLoaded] = useState(false);
    const contextRef = useRef(null);
    const [languages, setLanguages] = useState<ProgrammingLanguageEntry[]>([]);
    const [submitting, setSubmitting] = useState(false);
    useDocumentTitle(`${data?.title || '加载中'} - 比赛题目`);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    const [data, languages] = await Promise.all([
                        contestClient.getContestProblemDetail(
                            parseInt(problemID), numberContestID, virtualID
                        ),
                        utilClient.getSupportedLanguages()
                    ]);
                    setData(data);
                    setLanguages(languages)
                    setLoaded(true);
                } catch { } finally {
                }
            })();
        }
    }, [loaded, numberContestID, problemID, virtualID]);
    const handleSubmit = (code: string, language: string, parameters: number[]) => {
        const doNext = async () => {
            if (data === null) return;
            try {
                setSubmitting(true);
                const subid = await problemClient.submit(
                    data.id,
                    code,
                    language,
                    parameters,
                    numberContestID,
                    virtualID === -1 ? undefined : virtualID
                );
                window.location.href = `/show_submission/${subid}`;
            } catch { } finally {
                setSubmitting(false);
            }
        };
        if (code === "") {
            showConfirm("您确认要提交空代码吗?", doNext);
        } else doNext();
    };
    return <>
        {!loaded && <div style={{ height: "400px" }}>
            <Dimmer active>
                <Loader></Loader>
            </Dimmer>
        </div>}
        {loaded && data !== null && <>
            <Header as="h1">
                #{data.id + 1}. {data.title}
            </Header>
            <Segment style={{ maxWidth: "80%" }}
            >
                <Ref innerRef={contextRef}>
                    <div>
                        <div>
                            <ProblemStatementView
                                data={data}
                            ></ProblemStatementView>
                            {submitting && <Dimmer active>
                                <Loader></Loader>
                            </Dimmer>}
                            {data.problem_type !== "submit_answer" ? <CodeInput
                                defaultCode={data.last_code}
                                defaultLanguage={data.last_lang === "" ? languages[0].id : data.last_lang}
                                languages={languages}
                                usedParameters={data.usedParameters}
                                parameters={data.extra_parameter}
                                handleSubmit={handleSubmit}
                            ></CodeInput> : <div>
                                <Grid centered columns="3">
                                    <Grid.Column>
                                        <Button as="a" target="_blank" rel="noreferrer" href={`/submit_answer/${data.id}?contest=${contestID}&virtualID=${virtualID}`} icon color="green" labelPosition="left" >
                                            <Icon name="paper plane outline"></Icon>
                                            提交答案
                                        </Button>
                                    </Grid.Column>
                                </Grid>
                            </div>}
                        </div>
                        <Rail position="right">
                            <Sticky context={contextRef}>
                                <Segment stacked style={{ maxWidth: "300px" }}>
                                    <Table
                                        basic="very"
                                        collapsing
                                        celled
                                    >
                                        <Table.Body>
                                            <Table.Row>
                                                <Table.Cell>题目满分</Table.Cell>
                                                <Table.Cell>{data.score}</Table.Cell>
                                            </Table.Row>
                                            {data.using_file_io && <Table.Row>
                                                <Table.Cell>输入/输出文件</Table.Cell>
                                                <Table.Cell>{data.input_file_name}<br />{data.output_file_name}</Table.Cell>
                                            </Table.Row>}
                                        </Table.Body>
                                    </Table>
                                    {data.downloads.length !== 0 && <FileDownloadArea data={data} urlMaker={s => `/api/contest/${contestID}/${problemID}/download_file/${s}`}></FileDownloadArea>}
                                </Segment>
                            </Sticky>
                        </Rail>
                    </div>
                </Ref>
            </Segment>
        </>}
    </>
};

export default ContestProblem;