import React from "react";
import { Table } from "semantic-ui-react";
import { SettingPreview } from "../client/types";

const ConfigPreviewTab: React.FC<{ data: SettingPreview }> = ({ data }) => {

    return <div>
        <Table basic="very" celled>
            <Table.Header>
                <Table.Row>
                    <Table.HeaderCell>配置名</Table.HeaderCell>
                    <Table.HeaderCell>值</Table.HeaderCell>
                    <Table.HeaderCell>描述</Table.HeaderCell>
                </Table.Row>
            </Table.Header>
            <Table.Body>
                {data.map((x, i) => <Table.Row key={i}>
                    <Table.Cell>{x.key}</Table.Cell>
                    <Table.Cell>{typeof x.value === "boolean" ? JSON.stringify(x.value) : x.value}</Table.Cell>
                    <Table.Cell>{x.description}</Table.Cell>
                </Table.Row>)}
            </Table.Body>
        </Table>
    </div>;
};

export default ConfigPreviewTab;