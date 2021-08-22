import React, { useState } from "react";
import { Button, Dropdown, Form, Grid, Modal } from "semantic-ui-react";
import "ace-builds/src-noconflict/mode-plain_text";
import "ace-builds/src-noconflict/theme-github";
import AceEditor from "react-ace";
import { useAceTheme } from "../../states/StateUtils";
import _ from "lodash";
import { showConfirm } from "../../dialogs/Dialog";
interface BatchAddResponse {
    name: string;
    url: string;
}
const BatchAddDialog: React.FC<{
    open: boolean;
    onClose: () => void;
    finish: (resp: BatchAddResponse[]) => void;
}> = ({
    finish,
    onClose,
    open
}) => {
        const theme = useAceTheme();
        const [value, setValue] = useState("");
        const [format, setFormat] = useState("");
        const [options, setOptions] = useState([
            { key: "luogu", text: "https://www.luogu.com.cn/problem/#", value: "https://www.luogu.com.cn/problem/#" },
            { key: "cf", text: "https://codeforces.com/problemset/problem/#", value: "https://codeforces.com/problemset/problem/#" },
            { key: "default", text: "#", value: "#" },

        ]);
        const save = () => {
            const lines = value.split("\n").filter(x => x.trim() !== "");
            const splitted = lines.map(x => x.split(" "));
            const result: BatchAddResponse[] = [];
            const fmt = format === "" ? "#" : format;
            for (const item of splitted) {
                const front = _.initial(item);
                const tail = _.last(item)!;
                result.push({
                    name: front.join(" "),
                    url: fmt.replace(/#/g, tail)
                });
            }
            showConfirm(`您确定要添加共计 ${result.length} 条记录吗?`, () => {
                finish(result);
                onClose();
            });
        };
        return <Modal size="tiny" open={open} onClose={onClose}>
            <Modal.Header>
                批量添加外部题目
            </Modal.Header>
            <Modal.Content>
                <AceEditor
                    placeholder="每行表示一条数据，格式为'题目名 题号或链接'"
                    onChange={d => setValue(d)}
                    value={value}
                    theme={theme}
                    mode="plain_text"
                ></AceEditor>
                <Grid>
                    <Grid.Column>
                        <Form>
                            <Form.Field>
                                <label>题目链接模板</label>
                                <Dropdown
                                    options={options}
                                    placeholder="输入题目链接模板(使用#作为题号占位符)"
                                    search
                                    selection
                                    fluid
                                    allowAdditions
                                    additionLabel="自定义链接: "
                                    value={format}
                                    onChange={(e, { value }) => setFormat(value as string)}
                                    onAddItem={(_, { value }) => {
                                        setOptions([...options, { key: value as string, text: value as string, value: value as string }])
                                    }}
                                ></Dropdown>
                            </Form.Field>
                        </Form>
                    </Grid.Column>
                </Grid>
            </Modal.Content>
            <Modal.Actions>
                <Button color="green" onClick={save}>
                    保存
                </Button>
                <Button color="red" onClick={onClose}>
                    取消
                </Button>

            </Modal.Actions>
        </Modal>;
    };

export default BatchAddDialog;