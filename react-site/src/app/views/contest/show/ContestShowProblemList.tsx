import React from "react";
import { Link } from "react-router-dom";
import { Header, Segment, Table } from "semantic-ui-react";
import { PUBLIC_URL } from "../../../App";
import JudgeStatusLabel from "../../utils/JudgeStatusLabel";
import { ContestShowDetailResponse, RankCriterion } from "../client/types";

interface ContestShowProblemListProps {
    problems: ContestShowDetailResponse["problems"];
    rankCriterion: RankCriterion;
    contestID: number;
    virtualID: number;
    closed: boolean;
    running: boolean;
    status: number;
};

const ContestShowProblemList: React.FC<ContestShowProblemListProps> = ({
    problems,
    rankCriterion,
    contestID,
    virtualID,
    closed,
    running,
    status
}) => {
    const showWeightColumn = (rankCriterion === "last_submit" || rankCriterion === "max_score");
    return <>
        <Header as="h3">
            题目列表
        </Header>
        <Segment stacked>
            <Table basic="very" celled>
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell style={{ maxWidth: "100px" }}>我的提交</Table.HeaderCell>
                        <Table.HeaderCell>题目</Table.HeaderCell>
                        {showWeightColumn && <Table.HeaderCell>分数权值</Table.HeaderCell>}
                        <Table.HeaderCell>统计信息</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {problems.map((x, i) => <Table.Row
                        positive={x.status === "accepted"}
                        negative={x.status === "unaccepted"}
                        key={i}>
                        <Table.Cell style={{ maxWidth: "100px" }}>
                            <a href={x.my_submit !== -1 ? `/show_submission/${x.my_submit}` : undefined}>
                                <JudgeStatusLabel status={x.status}></JudgeStatusLabel>
                            </a>
                        </Table.Cell>
                        <Table.Cell>
                            <Link to={(status >= 1) ? `${PUBLIC_URL}/show_problem/${x.rawID}` : `${PUBLIC_URL}/contest/${contestID}/problem/${x.id}?virtual_contest=${virtualID}`}>
                                #{parseInt(x.id as unknown as string) + 1}. {x.title}
                            </Link>
                        </Table.Cell>
                        {showWeightColumn && <Table.Cell>{x.weight}</Table.Cell>}
                        <Table.Cell>
                            {x.accepted_submit !== -1 && <div>
                                {x.accepted_submit} / {x.total_submit} / {x.total_submit === 0 ? "无提交" : `${Math.ceil(100 * x.accepted_submit / x.total_submit)}%`}
                            </div>}
                        </Table.Cell>
                    </Table.Row>)}
                </Table.Body>
            </Table>
        </Segment>
    </>;
};

export default ContestShowProblemList;