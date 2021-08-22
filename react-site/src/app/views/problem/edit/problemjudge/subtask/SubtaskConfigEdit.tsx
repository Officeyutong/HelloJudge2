import React, { useEffect, useState } from "react";
import AceEditor from "react-ace";
import { Button, Modal } from "semantic-ui-react";
import { useAceTheme } from "../../../../../states/StateUtils";
import { ProblemFileEntry, SubtaskEntry } from "../../../client/types";
import { Schema, validate } from "jsonschema";
import "ace-builds/src-noconflict/mode-json";
import { showErrorModal } from "../../../../../dialogs/Dialog";
interface SubtaskConfigEditProps {
    files: ProblemFileEntry[];
    config: SubtaskEntry[];
    onUpdate: (cfg: SubtaskEntry[]) => void;
    onClose: () => void;
};

const makeSchemaWithFiles = (files: ProblemFileEntry[]): Schema => {
    const fileNames = files.map(x => x.name);
    return ({
        id: "SubtaskConfig",
        type: "array",
        items: {
            properties: {
                name: { type: "string" },
                score: { type: "integer", minimum: 0 },
                method: {
                    type: "string",
                    enum: ["min", "sum"]
                },
                testcases: {
                    type: "array",
                    items: {
                        properties: {
                            input: {
                                type: "string",
                                enum: fileNames
                            },
                            output: {
                                type: "string",
                                enum: fileNames
                            },
                            full_Score: {
                                type: "integer",
                                minimum: 0
                            }
                        },
                        required: ["input", "output"]
                    }
                },
                time_limit: {
                    type: "integer", minimum: 0
                },
                memory_limit: {
                    type: "integer", minimum: 4
                }
            },
            required: ["name", "score", "method", "testcases", "time_limit", "memory_limit"]
        }
    });
};
const SubtaskConfigEdit: React.FC<SubtaskConfigEditProps> = (props) => {
    const theme = useAceTheme();
    const [text, setText] = useState<string>(() => {
        const config = props.config.map(x => ({
            ...x, testcases: x.testcases.map(y => ({
                input: y.input, output: y.output
            }))
        }));
        return JSON.stringify(config, null, 4);
    });
    const [schema, setSchema] = useState<Schema>(() => makeSchemaWithFiles(props.files));
    useEffect(() => {
        setSchema(makeSchemaWithFiles(props.files));
    }, [props.files]);
    const save = () => {
        let parseRet;
        try {
            parseRet = JSON.parse(text);
        } catch (e) {
            showErrorModal(String(e), "请输入合法的JSON!");
            return;
        }
        const validateRet = validate(parseRet, schema);
        if (!validateRet.valid) {
            showErrorModal(validateRet.toString(), "请输入正确的子任务配置!");
            return;
        }
        const thisConfig: SubtaskEntry[] = parseRet.map((x: any) => ({
            ...x, testcases: x.testcases.map((y: any) => ({
                input: y.input, output: y.output, full_score: 0
            }))
        }));
        props.onUpdate(thisConfig);
        props.onClose();
    };
    return <Modal size="tiny" open>
        <Modal.Header>
            编辑子任务配置
        </Modal.Header>
        <Modal.Content>
            <AceEditor
                value={text}
                onChange={t => setText(t)}
                theme={theme}
                mode="json"
                width="100%"
                height="600px"
            ></AceEditor>
        </Modal.Content>
        <Modal.Actions>
            <Button color="red" onClick={props.onClose}>
                取消
            </Button>
            <Button color="green" onClick={save}>
                确定
            </Button>
        </Modal.Actions>
    </Modal>
};

export default SubtaskConfigEdit;