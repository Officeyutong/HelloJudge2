import _ from "lodash";
import { Button, Checkbox, Header, Input, Message, Segment, Table } from "semantic-ui-react";
import { ProblemDataProps } from "./ProblemJudgeTab";

const ExtraParameterConfig: React.FC<{
    data: ProblemDataProps["extra_parameter"];
    onUpdate: (data: ProblemDataProps["extra_parameter"]) => void;
}> = ({
    data,
    onUpdate
}) => {
        const update = onUpdate;
        return <>
            <Header as="h3">
                附加编译参数设定
            </Header>
            <Segment>
                <Table basic="very" celled>
                    <Table.Header>
                        <Table.Row>
                            <Table.HeaderCell>语言正则表达式</Table.HeaderCell>
                            <Table.HeaderCell>参数</Table.HeaderCell>
                            <Table.HeaderCell>名称</Table.HeaderCell>
                            <Table.HeaderCell>强制选中</Table.HeaderCell>
                            <Table.HeaderCell>操作</Table.HeaderCell>
                        </Table.Row>
                    </Table.Header>
                    <Table.Body>
                        {data.map((x, i) => <Table.Row key={i}>
                            <Table.Cell>
                                <Input value={x.lang} onChange={(e, d) => update(_.set([...data], i, { ...x, lang: d.value }))}></Input>
                            </Table.Cell>
                            <Table.Cell>
                                <Input value={x.parameter} onChange={(e, d) => update(_.set([...data], i, { ...x, parameter: d.value }))}></Input>
                            </Table.Cell>
                            <Table.Cell>
                                <Input value={x.name} onChange={(e, d) => update(_.set([...data], i, { ...x, name: d.value }))}></Input>
                            </Table.Cell>
                            <Table.Cell>
                                <Checkbox toggle checked={x.force} onChange={(e, d) => update(_.set([...data], i, { ...x, force: !x.force }))}></Checkbox>
                            </Table.Cell>
                            <Table.Cell>
                                <Button size="tiny" color="red" onClick={() => update(data.filter((y, j) => j !== i))}>
                                    删除
                                </Button>
                            </Table.Cell>
                        </Table.Row>)}
                        <Table.Row>
                            <Table.Cell></Table.Cell>
                            <Table.Cell></Table.Cell>
                            <Table.Cell></Table.Cell>
                            <Table.Cell></Table.Cell>
                            <Table.Cell><Button color="green" onClick={() => update([...data, { force: false, lang: ".*", name: "参数名", parameter: "" }])}>添加</Button></Table.Cell>
                        </Table.Row>
                    </Table.Body>
                </Table>
                <Message info>
                    <Message.Header>提示</Message.Header>
                    <Message.Content>
                        强制选中: 用户在提交代码时必须使用该编译参数
                    </Message.Content>
                </Message>
            </Segment>
        </>
    };


export default ExtraParameterConfig;