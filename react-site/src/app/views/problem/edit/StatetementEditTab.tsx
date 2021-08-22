import _ from "lodash";
import React, { Fragment } from "react";
import { Button, Divider, Form, Grid, Input } from "semantic-ui-react";
import SimpleAceWrapper from "../../utils/SimpleAceWrapper";
import { ProblemEditStatement } from "../client/types";
import ProblemStatementView from "../ProblemStatementView";

interface StatementEditProps extends ProblemEditStatement {
    id: number;
    onUpdate: (data: ProblemEditStatement) => void;
};

const StatementEditTab: React.FC<StatementEditProps> = (props) => {
    const {
        id,
        onUpdate
    } = props;
    const data: ProblemEditStatement = {
        background: props.background,
        content: props.content,
        example: props.example,
        hint: props.hint,
        input_format: props.input_format,
        output_format: props.output_format,
        title: props.title
    };;
    const update = onUpdate;
    return <div style={{ width: "100%" }}>
        <Grid columns="2">
            <Grid.Column width="8">
                <Form>
                    <Form.Field>
                        <label>题目ID</label>
                        {id}
                    </Form.Field>
                    <Form.Field>
                        <label>题目名</label>
                        <Input value={data.title} onChange={(e, d) => update({ ...data, title: d.value })}></Input>
                    </Form.Field>
                    <Form.Field>
                        <label>题目背景</label>
                        <SimpleAceWrapper
                            mode="markdown"
                            onChange={d => update({ ...data, background: d })}
                            value={data.background}
                        ></SimpleAceWrapper>
                    </Form.Field>
                    <Form.Field>
                        <label>题目内容</label>
                        <SimpleAceWrapper
                            mode="markdown"
                            onChange={d => update({ ...data, content: d })}
                            value={data.content}
                        ></SimpleAceWrapper>
                    </Form.Field>
                    <Form.Field>
                        <label>输入格式</label>
                        <SimpleAceWrapper
                            mode="markdown"
                            onChange={d => update({ ...data, input_format: d })}
                            value={data.input_format}
                        ></SimpleAceWrapper>
                    </Form.Field>
                    <Form.Field>
                        <label>输出格式</label>
                        <SimpleAceWrapper
                            mode="markdown"
                            onChange={d => update({ ...data, output_format: d })}
                            value={data.output_format}
                        ></SimpleAceWrapper>
                    </Form.Field>
                    {data.example.map((x, i) => <Fragment key={i}>
                        <Form.Group widths="equal">
                            <Form.Field>
                                <label>样例 {i + 1} 输入</label>
                                <SimpleAceWrapper
                                    mode="plain_text"
                                    value={x.input}
                                    onChange={d => update({ ...data, example: _.set([...data.example], i, { input: d, output: x.output }) })}
                                ></SimpleAceWrapper>
                            </Form.Field>
                            <Form.Field>
                                <label>样例 {i + 1} 输出</label>
                                <SimpleAceWrapper
                                    mode="plain_text"
                                    value={x.output}
                                    onChange={d => update({ ...data, example: _.set([...data.example], i, { output: d, input: x.input }) })}
                                ></SimpleAceWrapper>
                            </Form.Field>
                        </Form.Group>
                        <Button size="tiny" color="red" onClick={() => update({ ...data, example: data.example.filter((v, j) => j !== i) })}>
                            删除本组
                        </Button>
                    </Fragment>)}
                    <div style={{ marginTop: "10px" }}>
                        <Button size="tiny" color="green" onClick={() => update({ ...data, example: [...data.example, { input: "样例输入", output: "样例输出" }] })}>添加样例</Button>
                    </div>
                    <Divider></Divider>
                    <Form.Field>
                        <label>提示</label>
                        <SimpleAceWrapper
                            mode="markdown"
                            value={data.hint}
                            onChange={d => update({ ...data, hint: d })}
                        ></SimpleAceWrapper>
                    </Form.Field>
                </Form>
                <Divider></Divider>
            </Grid.Column>
            <Grid.Column width="8">
                <ProblemStatementView
                    data={{ ...data, id: id }}
                    showSubtasks={false}
                ></ProblemStatementView>
            </Grid.Column>

        </Grid>
        <Divider vertical></Divider>
    </div>;
};
export default StatementEditTab;

// const mapData = (d: ProblemEditStatement): any[] => {
//     return [
//         d.background, d.content, d.example, d.hint, d.input_format, d.output_format, d.title
//     ];
// };

// export default React.memo(StatementEditTab, (prev, next) => {
//     const a1 = mapData(prev.data);
//     const a2 = mapData(next.data);
//     for (let i = 0; i < a1.length; i++) {
//         if (a1[i] !== a2[i]) return false;
//     }
//     return true;
// });