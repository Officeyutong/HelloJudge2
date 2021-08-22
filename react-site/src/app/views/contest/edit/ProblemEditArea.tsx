import _ from "lodash";
import { Button, Icon, Input, Message, Table } from "semantic-ui-react";
import { ContestEditRawDataResponse } from "../client/types";


type Problems = ContestEditRawDataResponse["problems"];
interface ProblemEditAreaProps {
    data: Problems;
    update: (data: Problems) => void;
};


const ProblemEditArea: React.FC<ProblemEditAreaProps> = ({ data, update }) => {

    return <>
        <Table celled>
            <Table.Header>
                <Table.Row>
                    <Table.HeaderCell>题目ID</Table.HeaderCell>
                    <Table.HeaderCell>分数权值</Table.HeaderCell>
                    <Table.HeaderCell>操作</Table.HeaderCell>
                </Table.Row>
            </Table.Header>
            <Table.Body>
                {data.map((x, i) => <Table.Row key={i}>
                    <Table.Cell>
                        <Input value={x.id} type="number" onChange={(e, d) => update(_.set([...data], i, { ...x, id: parseInt(d.value) }))}></Input>
                    </Table.Cell>
                    <Table.Cell>
                        <Input value={x.weight} type="number" onChange={(e, d) => update(_.set([...data], i, { ...x, weight: parseInt(d.value) }))}></Input>
                    </Table.Cell>
                    <Table.Cell>
                        <Button.Group>
                            <Button onClick={() => {
                                const arr = [...data];
                                [arr[i], arr[i - 1]] = [arr[i - 1], arr[i]];
                                update(arr);
                            }} icon color="blue" disabled={i === 0}>
                                <Icon name="angle up"></Icon>
                            </Button>
                            <Button onClick={() => {
                                const arr = [...data];
                                [arr[i], arr[i + 1]] = [arr[i + 1], arr[i]];
                                update(arr);
                            }} icon color="blue" disabled={i === data.length - 1}>
                                <Icon name="angle down"></Icon>
                            </Button>
                            <Button icon color="green" onClick={() => {
                                update(data.filter((_, j) => j !== i))
                            }} >
                                <Icon name="times"></Icon>
                            </Button>
                        </Button.Group>
                    </Table.Cell>
                </Table.Row>)}
                <Table.Row>
                    <Table.Cell colSpan="2">
                        <Message info>
                            <Message.Header>提示</Message.Header>
                            <Message.Content>
                                比赛中的题目分数 = 题目实际得分 * 分数权值
                            </Message.Content>
                        </Message>
                    </Table.Cell>
                    <Table.Cell>
                        <Button color="green" onClick={() => update([...data, { id: (_(data).map(x => x.id).max() || 0) + 1, weight: 1 }])}>
                            添加题目
                        </Button>
                    </Table.Cell>
                </Table.Row>
            </Table.Body>
        </Table>

    </>;
};

export default ProblemEditArea;