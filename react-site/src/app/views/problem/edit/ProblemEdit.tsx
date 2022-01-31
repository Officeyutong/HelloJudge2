import React, { lazy, Suspense, useEffect, useRef, useState } from "react";
import { useParams } from "react-router";
import { Link } from "react-router-dom";
import { Button, Dimmer, Header, Loader, Modal, Segment, Tab } from "semantic-ui-react";
import { PUBLIC_URL } from "../../../App";
import { useDocumentTitle } from "../../../common/Utils";
import { showSuccessModal } from "../../../dialogs/Dialog";
import GeneralDimmedLoader from "../../utils/GeneralDimmedLoader";
import problemClient from "../client/ProblemClient";
import { ProblemEditReceiveInfo } from "../client/types";
const PermissionEdit = lazy(() => import("./PermissionEditTab"));
const ProblemFilesEditTab = lazy(() => import("./ProblemFilesEditTab"));
const ProblemJudgeTab = lazy(() => import("./problemjudge/ProblemJudgeTab"));
const ProblemTags = lazy(() => import("./ProblemTagsTab"));
const StatementEditTab = lazy(() => import("./StatetementEditTab"));
const ProblemEdit: React.FC<{}> = () => {
    const { problemID } = useParams<{ problemID: string }>();
    const numberID = parseInt(problemID);
    const [loaded, setLoaded] = useState(false);
    const [data, setData] = useState<ProblemEditReceiveInfo | null>(null);
    const [submitAnswer, setSubmitAnswer] = useState(false);
    const [saving, setSaving] = useState(false);
    const savingRef = useRef<boolean>(false);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    const resp = await problemClient.getProblemInfo(numberID, true);
                    for (const subtask of resp.subtasks) {
                        subtask.memory_limit = parseInt(String(subtask.memory_limit));
                        subtask.time_limit = parseInt(String(subtask.time_limit));
                    }
                    resp.files.sort((x, y) => {
                        if (x.name < y.name) return -1;
                        else if (x.name === y.name) return 0;
                        else return 1;
                    });
                    setLoaded(true);
                    setSubmitAnswer(resp.problem_type === "submit_answer");
                    setData(resp);
                } catch { } finally { }
            })();
        }
    }, [loaded, numberID]);
    useDocumentTitle(data !== null ? `${data.title} - 题目编辑` : "加载中...");
    const handleSave = async () => {
        if (data === null) return;
        if (savingRef.current) return;
        try {
            setSaving(true);
            savingRef.current = true;
            await problemClient.updateProblemInfo(numberID, {
                background: data!.background,
                can_see_results: data!.can_see_results,
                content: data.content,
                downloads: data.downloads,
                example: data.example,
                extra_parameter: data.extra_parameter,
                hint: data.hint,
                id: data.id,
                input_file_name: data.input_file_name,
                input_format: data.input_format,
                invite_code: data.invite_code,
                newProblemID: data.id,
                output_file_name: data.output_file_name,
                output_format: data.output_format,
                provides: data.provides,
                public: data.public,
                spj_filename: data.spj_filename,
                submissionVisible: data.submissionVisible,
                subtasks: data.subtasks,
                title: data.title,
                using_file_io: data.using_file_io
            }, submitAnswer);
            showSuccessModal("保存成功!");
        } catch { } finally {
            setSaving(false);
            savingRef.current = false;
        }
    };
    const onProblemDataUpdate = (d: any) => {
        setData({ ...data, ...d });
    };
    return <div>

        {loaded && data !== null ? <>
            <Header as="h1">
                #{data.id} - {data.title}
            </Header>
            <Tab
                renderActiveOnly={false}
                panes={[
                    {
                        menuItem: "题面",
                        pane: <Tab.Pane key={0}>
                            <Suspense
                                fallback={<GeneralDimmedLoader />}
                            >
                                <StatementEditTab
                                    {...data}
                                    onUpdate={onProblemDataUpdate}
                                ></StatementEditTab>
                            </Suspense>
                        </Tab.Pane>
                    },
                    {
                        menuItem: "题目权限设定",
                        pane: <Tab.Pane key={1}>
                            <Suspense fallback={<GeneralDimmedLoader />}>
                                <PermissionEdit
                                    {...data}
                                    onUpdate={onProblemDataUpdate}
                                ></PermissionEdit>
                            </Suspense>
                        </Tab.Pane>
                    },
                    {
                        menuItem: "题目标签设定",
                        pane: <Tab.Pane key={2}>
                            <Suspense fallback={<GeneralDimmedLoader />}>
                                <ProblemTags
                                    id={numberID}
                                    defaultTags={data.tags}
                                ></ProblemTags>
                            </Suspense>
                        </Tab.Pane>
                    },
                    {
                        menuItem: "题目文件设定",
                        pane: <Tab.Pane key={3}>
                            <Suspense fallback={<GeneralDimmedLoader />}>
                                <ProblemFilesEditTab
                                    {...data}
                                    onUpdate={onProblemDataUpdate}
                                ></ProblemFilesEditTab>
                            </Suspense>
                        </Tab.Pane>
                    },
                    {
                        menuItem: "评测设定",
                        pane: <Tab.Pane key={4}>
                            <Suspense fallback={<GeneralDimmedLoader />}>
                                <ProblemJudgeTab
                                    extra_parameter={data.extra_parameter}
                                    files={data.files}
                                    id={data.id}
                                    input_file_name={data.input_file_name}
                                    output_file_name={data.output_file_name}
                                    problem_type={data.problem_type}
                                    spj_filename={data.spj_filename}
                                    subtasks={data.subtasks}
                                    using_file_io={data.using_file_io}
                                    submitAnswer={submitAnswer}
                                    onUpdateSubmitAnswer={setSubmitAnswer}
                                    onUpdate={onProblemDataUpdate}
                                ></ProblemJudgeTab>
                            </Suspense>
                        </Tab.Pane>
                    },
                ]}
            ></Tab>
            <Button style={{ marginTop: "10px" }} color="green" onKeyDown={() => { }} onClick={handleSave}>
                保存
            </Button>
            <Button style={{ marginTop: "10px" }} color="green" as={Link} to={`${PUBLIC_URL}/show_problem/${data.id}`}>
                返回题目
            </Button>
        </> : <Segment>
            <div style={{ height: "400px" }}>
                <Dimmer active>
                    <Loader></Loader>
                </Dimmer>
            </div>
        </Segment>}
        {saving && <Modal basic open closeOnDimmerClick={false}>
            <Modal.Header>
                保存中
            </Modal.Header>
            <Modal.Content>
                <Loader></Loader>
            </Modal.Content>
        </Modal>}
    </div>;
}

export default ProblemEdit;