import React from "react";
import { Button, Container, Grid, Header, Icon, Segment, Table } from "semantic-ui-react";
import { ProblemStatement } from "./client/types";
import * as clipboard from "clipboardy";
import { converter } from "../../common/Markdown";
import "./ProblemMeta.css";
const ProblemMetaBlock: React.FC<{ value: string; name: string; preBlock?: boolean; withCopy?: boolean }> = ({ name, preBlock, value, withCopy }) => {
    const innerHTML = preBlock === undefined ? converter.makeHtml(value) : value;
    return <div>
        {value !== "" && <>
            <Container className="problem-meta">
                <Grid columns="2">
                    <Grid.Column><Header as="h3">{name}</Header></Grid.Column>
                    {withCopy !== undefined && <Grid.Column textAlign="right">
                        <Button size="tiny" circular color="orange" icon onClick={() => clipboard.write(value)}><Icon name="clipboard outline"></Icon></Button>
                    </Grid.Column>}
                </Grid>
                <Segment>
                    {preBlock !== undefined ? <pre style={{ whiteSpace: "pre-wrap", wordBreak: "break-word" }} dangerouslySetInnerHTML={{ __html: innerHTML }}></pre> : <div dangerouslySetInnerHTML={{ __html: innerHTML }}></div>}
                </Segment>
            </Container>
        </>}
    </div>;
};

const ProblemStatementView: React.FC<{
    data: Omit<ProblemStatement, "subtasks"> & { subtasks?: ProblemStatement["subtasks"] };
    showSubtasks?: boolean;
}> = ({ data, showSubtasks }) => {
    const willShowSubtask = (showSubtasks === undefined) ? true : showSubtasks;
    return <>
        <ProblemMetaBlock name="题目背景" value={data.background} withCopy={false}></ProblemMetaBlock>
        <ProblemMetaBlock name="题目内容" value={data.content} withCopy={false}></ProblemMetaBlock>
        <ProblemMetaBlock name="输入格式" value={data.input_format} withCopy={false}></ProblemMetaBlock>
        <ProblemMetaBlock name="输出格式" value={data.output_format} withCopy={false}></ProblemMetaBlock>
        {data.example.map((x, i) => <Grid columns="2" key={i}>
            <Grid.Column>
                <ProblemMetaBlock name={`样例 ${i + 1} 输入`} value={x.input} withCopy preBlock></ProblemMetaBlock>
            </Grid.Column>
            <Grid.Column>
                <ProblemMetaBlock name={`样例 ${i + 1} 输出`} value={x.output} withCopy preBlock></ProblemMetaBlock>
            </Grid.Column>
        </Grid>)}
        {willShowSubtask && <div className="problem-meta">
            <Header as="h3">
                子任务
            </Header>
            <Table>
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell>子任务名</Table.HeaderCell>
                        <Table.HeaderCell>评分方式</Table.HeaderCell>
                        <Table.HeaderCell>时间限制</Table.HeaderCell>
                        <Table.HeaderCell>内存限制</Table.HeaderCell>
                        <Table.HeaderCell>说明</Table.HeaderCell>
                        <Table.HeaderCell>分数</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {data.subtasks!.map((x, i) => <Table.Row key={i}>
                        <Table.Cell>{x.name}</Table.Cell>
                        <Table.Cell>{{ min: "取最小值", sum: "求和" }[x.method]}</Table.Cell>
                        <Table.Cell>{x.time_limit} ms</Table.Cell>
                        <Table.Cell>{x.memory_limit} MB</Table.Cell>
                        <Table.Cell><div dangerouslySetInnerHTML={{ __html: converter.makeHtml(x.comment) }}></div></Table.Cell>
                        <Table.Cell>{x.score}</Table.Cell>
                    </Table.Row>)}
                </Table.Body>
            </Table>
        </div>}
        <ProblemMetaBlock name="提示" value={data.hint} withCopy={false}></ProblemMetaBlock>
    </>;
};


export default ProblemStatementView;