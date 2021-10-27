import { Button, Container, Input, Table } from "semantic-ui-react";
import { useInputValue } from "../../../common/Utils";
import { showSuccessModal } from "../../../dialogs/Dialog";
import { TeamDetail } from "../client/types";

type TeamStuff = TeamDetail["team_problems"] | TeamDetail["team_contests"] | TeamDetail["team_problemsets"];

interface GeneralTeamStuffProps {
    data: TeamStuff;
    title?: string[];
    lineMapper: (data: TeamStuff[0]) => React.ReactNode[];
    addCallback: (text: string) => void;
    isTeamAdmin: boolean;
    promptButtonString: string;
};


const GeneralTeamStuff: React.FC<GeneralTeamStuffProps> = (props) => {
    const empty = props.data.length === 0;
    const inputValue = useInputValue();
    return <>
        {props.isTeamAdmin && <>
            <Input {...inputValue} placeholder="请在此输入相应ID，如果要添加多个请以英文逗号分开" fluid actionPosition="left" action={{
                color: "green",
                content: props.promptButtonString,
                onClick: (evt: any) => props.addCallback(inputValue.value)
            }} ></Input>
        </>}
        {empty ? <Container style={{ marginTop: "20px" }} textAlign="center">
            <span>没有数据...</span>
        </Container> : <>
            <Container style={{ marginTop: "10px" }} textAlign="right">
                <Button color="green" size="tiny" onClick={() => showSuccessModal("操作完成！")}>
                    解锁权限
                </Button>
            </Container>

            <Table
            >
                {props.title !== undefined && <Table.Header>
                    <Table.Row>
                        {props.title.map(x => <Table.HeaderCell key={x}>{x}</Table.HeaderCell>)}
                    </Table.Row>
                </Table.Header>}
                <Table.Body>
                    {props.data.map((x: any) => <Table.Row key={x.id}>
                        {props.lineMapper(x).map((y, i) => <Table.Cell key={i}>{y}</Table.Cell>)}
                    </Table.Row>)}
                </Table.Body>
            </Table>
        </>}
    </>
};

export default GeneralTeamStuff;