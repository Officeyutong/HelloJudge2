import { Schema, validate } from "jsonschema";
import _ from "lodash";
import { useEffect, useMemo, useRef, useState } from "react";
import { useSelector } from "react-redux";
import { Button, Checkbox, Container, Dimmer, Divider, Form, Grid, Header, Input, Loader, Menu, Segment } from "semantic-ui-react";
import { ProgrammingLanguageEntry } from "../../common/types";
import { useDocumentTitle } from "../../common/Utils";
import { StateType } from "../../states/Manager";
import utilClient from "../utils/client/UtilClient";
import { IDERunStoredData } from "./client/types";
import AceEditor from "react-ace";
import { useAceTheme } from "../../states/StateUtils";
import AnsiUp from "ansi_up";
import { showErrorModal } from "../../dialogs/Dialog";
import onlineIDEClient from "./client/OnlineIDEClient";
import "./OnlineIDE.css"
const StoredDataSchema: Schema = {
    properties: {
        code: { type: "string" },
        input: { type: "string" },
        lang: { type: "string" },
        parameter: { type: "string" }
    }
};
const ansiUp = new AnsiUp();
function loadStoredData(): IDERunStoredData | null {
    const obj = window.localStorage.getItem("hellojudge2-ide");
    if (!obj) return null;
    try {
        const decoded = JSON.parse(obj);
        if (!validate(decoded, StoredDataSchema).valid) return null;
        return decoded as IDERunStoredData;
    } catch { return null; }
}
function saveData(data: IDERunStoredData) {
    window.localStorage.setItem("hellojudge2-ide", JSON.stringify(data));
}
const OnlineIDE: React.FC<{}> = () => {
    const usePolling = useSelector((s: StateType) => s.userState.userData.usePolling);

    const [loading, setLoading] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const [languages, setLanguages] = useState<ProgrammingLanguageEntry[]>([]);

    const [code, setCode] = useState("");
    const [inputText, setInputText] = useState("");
    const fileRef = useRef<HTMLInputElement>(null);
    const [inputArgs, setInputArgs] = useState("");
    const [lang, setLang] = useState("");
    const theme = useAceTheme();

    const langMap = useMemo(() => new Map(languages.map(x => [x.id, x])), [languages]);
    const currLangObj = useMemo(() => langMap.get(lang)!, [lang, langMap]);
    const [useFileInput, setUseFileInput] = useState(false);
    const [output, setOutput] = useState("");
    const ansiTranslated = useMemo(() => ansiUp.ansi_to_html(output), [output]);
    const [submitting, setSubmitting] = useState(false);
    // const trackerTokenRef = useRef<NodeJS.Timeout | null>(null);
    useDocumentTitle("在线IDE");

    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setLoading(true);
                    const langs = await utilClient.getSupportedLanguages();
                    setLanguages(langs);
                    const storeData = loadStoredData();
                    if (storeData !== null) {
                        if (_(langs).map(x => x.id).includes(storeData.lang)) {
                            setLang(storeData.lang);
                        } else {
                            setLang(langs[0].id);
                        }
                        setInputArgs(storeData.parameter);
                        setInputText(storeData.input);
                        setCode(storeData.code);
                    } else {
                        setLang(langs[0].id);
                    }
                    setLoaded(true);
                    setLoading(false);
                } catch { }
            })();
        }
    }, [loaded]);
    const handleSubmit = async () => {
        if (submitting) return;
        if (!usePolling) {
            showErrorModal("暂未支持非轮询方式的在线IDE!");
            return;
        }
        try {
            setSubmitting(true);
            let inputData = inputText;
            if (useFileInput) {
                const files = fileRef.current!.files;
                if (files === null || files.length !== 1) {
                    setSubmitting(false);
                    showErrorModal("请选择恰好一个文件作为输入!");
                    return;
                }
                const selectedFile = files[0];
                if (selectedFile.size > 100 * 1024) {
                    setSubmitting(false);
                    showErrorModal("上传文件大小不可超过100KB!");
                    return;
                }
                inputData = await selectedFile.text();
            }
            saveData({
                input: useFileInput ? "" : inputData,
                code: code,
                lang: lang,
                parameter: inputArgs
            });
            const { run_id } = await onlineIDEClient.submit(code, inputData, lang, inputArgs);
            if (usePolling) {
                const token = setInterval(() => {
                    onlineIDEClient.fetchStatus(run_id).then(resp => {
                        if (resp.status === "done") {
                            clearInterval(token);
                            setSubmitting(false);
                        }
                        setOutput(resp.message);
                    }, () => clearInterval(token));
                }, 3000);
                setOutput("运行中...");
            }
        } catch { } finally {
        }
    };
    return <>
        <Header as="h1">
            在线IDE
        </Header>
        <Segment stacked>
            {loading && <div style={{ height: "400px" }}>
                <Dimmer active>
                    <Loader>加载中</Loader>
                </Dimmer>
            </div>}
            {loaded && <Grid columns="1">
                <Grid.Column>
                    <Grid columns="2">
                        <Grid.Column width="4">
                            <Menu
                                vertical
                                pointing
                                style={{ overflowY: "scroll", height: "500px", overflowX: "hidden" }}
                            >
                                {languages.map((x, i) => <Menu.Item key={i} active={lang === x.id} onClick={() => setLang(x.id)} as="a">
                                    <span>
                                        <Header as="h4">
                                            {x.display}
                                        </Header>
                                        {x.version}
                                    </span>
                                </Menu.Item>)}
                            </Menu>
                        </Grid.Column>
                        <Grid.Column width="12">
                            <AceEditor
                                onChange={v => setCode(v)}
                                value={code}
                                theme={theme}
                                mode={currLangObj.ace_mode}
                                fontSize="large"
                                width="100%"
                                wrapEnabled={true}
                            ></AceEditor>
                        </Grid.Column>
                    </Grid>
                    <Divider></Divider>
                </Grid.Column>
                <Grid.Column>
                    <Grid columns="2">
                        <Grid.Column>
                            <Header as="h3">
                                输入
                            </Header>
                            <Form>
                                <Form.Field>
                                    <Checkbox toggle label="使用文件输入" checked={useFileInput} onChange={(_, d) => setUseFileInput(d.checked!)}></Checkbox>
                                </Form.Field>
                                <Form.Field>
                                    {!useFileInput ? <AceEditor
                                        value={inputText}
                                        onChange={v => setInputText(v)}
                                        wrapEnabled={true}
                                        theme={theme}
                                        height="200px"
                                        width="100%"
                                    ></AceEditor> : <div>
                                        <input ref={fileRef} type="file"></input>
                                    </div>}
                                </Form.Field>
                                <Form.Field>
                                    <label>编译参数</label>
                                    <Input value={inputArgs} onChange={(_, d) => setInputArgs(d.value)}></Input>
                                </Form.Field>
                            </Form>

                        </Grid.Column>
                        <Grid.Column>
                            <Header as="h3">输出</Header>
                            <Segment>
                                <span dangerouslySetInnerHTML={{ __html: ansiTranslated }} className="raw-span">
                                </span>
                            </Segment>
                        </Grid.Column>
                    </Grid>
                </Grid.Column>
                <Grid.Column>
                    <Container textAlign="center">
                        <Button color="green" loading={submitting} onClick={handleSubmit}>
                            提交
                        </Button>
                    </Container>
                </Grid.Column>
            </Grid>}
        </Segment>
    </>;
}

export default OnlineIDE;