import React, { useEffect, useState } from "react";
import { Button, Checkbox, Grid, Header, Icon, Menu, Segment, Table } from "semantic-ui-react";
import { int, ProgrammingLanguageEntry } from "../../common/types";
import { ExtraParameterEntry } from "./client/types";
import AceEditor from "react-ace";
import { v4 as uuidv4 } from "uuid";
import { useAceTheme } from "../../states/StateUtils";
interface CodeInputProps {
    defaultCode: string;
    languages: ProgrammingLanguageEntry[];
    defaultLanguage: string;
    // onCurrentLanguageChange: (lang: string) => void;
    parameters: ExtraParameterEntry[];
    usedParameters: int[];
    // setCurrentParameters: (val: int[]) => void;
    handleSubmit: (code: string, language: string, parameters: number[]) => void;

};

const CodeInput: React.FC<CodeInputProps> = (props) => {
    const [code, setCode] = useState(props.defaultCode);
    const [currentLanguage, setCurrentLanguage] = useState(props.defaultLanguage);
    const [params, setParams] = useState<number[]>(props.usedParameters);
    const theme = useAceTheme();
    const [languageObj, setLanguageObj] = useState<ProgrammingLanguageEntry | null>(null);
    useEffect(() => {
        for (const item of props.languages) {
            if (item.id === currentLanguage) setLanguageObj(item);
        }
    }, [currentLanguage, props.languages]);
    return languageObj !== null ? <>
        <Grid columns="1">
            <Grid.Column>
                <Grid columns="2">
                    <Grid.Column width="4">
                        <Menu
                            vertical
                            pointing
                            style={{ overflowY: "scroll", height: "500px", maxWidth: "170px", overflowX: "hidden" }}
                        >
                            {props.languages.map((x, i) => <Menu.Item key={i} active={currentLanguage === x.id} onClick={() => setCurrentLanguage(x.id)} as="a">
                                <span>
                                    <Header as="h4">
                                        {x.display}
                                    </Header>
                                    {x.version}
                                </span>
                            </Menu.Item>)}
                        </Menu>
                    </Grid.Column>
                    <Grid.Column width="12" stretched>
                        <AceEditor
                            onChange={v => setCode(v)}
                            value={code}
                            name={uuidv4()}
                            theme={theme}
                            mode={languageObj?.ace_mode}
                            fontSize="large"
                            width="100%"
                        ></AceEditor>
                    </Grid.Column>

                </Grid>
            </Grid.Column>
            <Grid.Column>
                <Segment>
                    <Table celled basic="very">
                        <Table.Header>
                            <Table.Row>
                                <Table.HeaderCell>名称</Table.HeaderCell>
                                <Table.HeaderCell>参数</Table.HeaderCell>
                                <Table.HeaderCell></Table.HeaderCell>
                            </Table.Row>
                        </Table.Header>
                        <Table.Body>
                            {props.parameters.map((x, i) => (currentLanguage.match(x.lang)?.length || 0) !== 0 && <Table.Row key={i}>
                                <Table.Cell>{x.name}</Table.Cell>
                                <Table.Cell>{x.parameter}</Table.Cell>
                                <Table.Cell>
                                    <Checkbox disabled={x.force} toggle checked={params.includes(i) || x.force} onClick={() => {
                                        const checked = params.includes(i);
                                        if (checked) setParams(params.filter(x => x !== i));
                                        else setParams([...params, i]);
                                    }} label="使用"></Checkbox>
                                </Table.Cell>
                            </Table.Row>)}
                        </Table.Body>
                    </Table>
                </Segment>
            </Grid.Column>
            <Grid.Column>
                <Grid columns="3" centered>
                    <Grid.Column>
                        <Button icon color="green" labelPosition="left" onClick={() => props.handleSubmit(code, currentLanguage, params)}>
                            <Icon name="paper plane outline"></Icon>
                            提交
                        </Button>
                    </Grid.Column>
                </Grid>
            </Grid.Column>
        </Grid>
    </> : <></>
};

export default React.memo(CodeInput, (prev, next) => {
    return prev.defaultCode !== next.defaultCode || prev.defaultLanguage !== next.defaultLanguage || prev.languages !== next.languages || prev.parameters !== next.parameters || prev.usedParameters !== next.usedParameters;
});