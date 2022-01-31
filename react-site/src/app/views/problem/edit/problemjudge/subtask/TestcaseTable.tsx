import _ from "lodash";
import React, { useEffect, useState } from "react";
import { Button, Dropdown, Table } from "semantic-ui-react";
import { ProblemEditReceiveInfo } from "../../../client/types";

type TestcaseType = ProblemEditReceiveInfo["subtasks"][0]["testcases"];
type FilesType = ProblemEditReceiveInfo["files"];

interface TestcaseTableProps {
    testcases: TestcaseType;
    onUpdate: (d: TestcaseType) => void;
    files: FilesType
};

const TestcaseTable: React.FC<TestcaseTableProps> = ({
    testcases, onUpdate, files
}) => {
    const update = onUpdate;
    const [fileOptions, setFileOptions] = useState<{ key: string; text: string }[]>([]);
    const [fileNamesMapping, setFileNamesMapping] = useState<Map<string, string>>(new Map());
    useEffect(() => {
        const value = files.map(x => ({
            key: x.name,
            text: `${x.name}(${Math.ceil(x.size / 1024)}KB)`,
            value: x.name
        }));
        const mapping = new Map(value.map(x => ([x.key, x.text])));
        setFileOptions(value);
        setFileNamesMapping(mapping);
    }, [files]);
    return <Table>
        <Table.Header>
            <Table.Row>
                <Table.HeaderCell>ID</Table.HeaderCell>
                <Table.HeaderCell>输入文件名</Table.HeaderCell>
                <Table.HeaderCell>输出文件名</Table.HeaderCell>
                <Table.HeaderCell>操作</Table.HeaderCell>
            </Table.Row>
        </Table.Header>
        <Table.Body>
            {testcases.map((x, i) => <Table.Row key={i}>
                <Table.Cell>{i + 1}</Table.Cell>
                <Table.Cell>
                    <Dropdown
                        fluid
                        selection
                        options={fileOptions}
                        value={x.input}
                        text={fileNamesMapping.get(x.input)}
                        onChange={(e, d) => update(_.set([...testcases], i, { ...x, input: d.value }))}
                    ></Dropdown>
                </Table.Cell>
                <Table.Cell>
                    <Dropdown
                        fluid
                        selection
                        options={fileOptions}
                        value={x.output}
                        text={fileNamesMapping.get(x.output)}
                        onChange={(e, d) => update(_.set([...testcases], i, { ...x, output: d.value }))}
                    ></Dropdown>
                </Table.Cell>
                <Table.Cell>
                    <Button color="red" size="tiny" onClick={() => update(testcases.filter((y, j) => j !== i))}>
                        删除
                    </Button>
                </Table.Cell>
            </Table.Row>)}
            <Table.Row>
                <Table.Cell></Table.Cell>
                <Table.Cell></Table.Cell>
                <Table.Cell></Table.Cell>
                <Table.Cell>
                    <Button size="tiny" color="green" onClick={() => update([...testcases, { full_score: 0, input: "", output: "" }])}>
                        添加测试点
                    </Button>
                </Table.Cell>
            </Table.Row>
        </Table.Body>
    </Table>;
};


export default TestcaseTable;