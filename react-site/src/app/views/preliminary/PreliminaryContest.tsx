import _ from "lodash";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { useHistory, useParams } from "react-router-dom";
import { Button, Dimmer, Header, Icon, Loader, Message, Segment } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { useDocumentTitle } from "../../common/Utils";
import preliminaryClient from "./client/PreliminaryClient";
import { PreliminaryContestDetail } from "./client/types";
import ContestInfo from "./ContestInfo";
import FillBlankProblem from "./FillBlankProblem";
import SelectionProblem from "./SelectionProblem";

const PreliminaryContest: React.FC<{}> = () => {
    const { contest, problem } = useParams<{ contest: string; problem?: string; }>();
    const [data, setData] = useState<PreliminaryContestDetail | null>(null);
    const [loading, setLoading] = useState(false);
    const [answers, setAnswers] = useState<(string | string[])[][]>([]);
    useDocumentTitle(`${data?.title || "加载中..."} - 笔试题库`);
    useEffect(() => {
        (async () => {
            try {
                setLoading(true);
                const data = (await preliminaryClient.getContestDetail(parseInt(contest)));
                setAnswers(
                    data.problems.map(
                        t => t.questions.map(
                            () => t.problemType === "fill_blank" ? "" : []
                        )
                    )
                );
                setData(data);
                setLoading(false);
            } catch { } finally { }
        })();
    }, [contest]);
    const currProblem = useMemo(() => {
        if (problem === undefined || data === null) return null;
        const pid = parseInt(problem);
        const problemEntry = data.problems[pid];
        if (problemEntry === undefined) return null;
        return problemEntry;
    }, [problem, data]);
    const numberProblem = parseInt(problem || "0");
    const history = useHistory();
    const previousProblem = useCallback(() => history.push(`${PUBLIC_URL}/preliminary/contest/${contest}/${numberProblem - 1}`), [contest, history, numberProblem]);
    const nextProblem = useCallback(() => history.push(`${PUBLIC_URL}/preliminary/contest/${contest}/${numberProblem + 1}`), [contest, history, numberProblem]);
    const keyDownHandler = useCallback((evt: KeyboardEvent) => {
        if (problem === undefined || data === null) return;
        const key = evt.key;
        if (key === "ArrowLeft") {
            if (numberProblem !== 0) previousProblem();
        } else if (key === "ArrowRight") {
            if (numberProblem !== data.problems.length - 1) nextProblem();
        }
    }, [data, nextProblem, numberProblem, previousProblem, problem]);
    useEffect(() => {
        window.addEventListener("keydown", keyDownHandler);
        return () => window.removeEventListener("keydown", keyDownHandler);
    }, [keyDownHandler]);
    return <>
        {loading && <>
            <Segment>
                <div style={{ height: "400px" }}></div>
                <Dimmer active>
                    <Loader></Loader>
                </Dimmer>
            </Segment>
        </>}
        {data !== null && <>
            <Header as="h1">
                {data.title}
            </Header>
            {problem === undefined ? <ContestInfo
                {...data}
                id={parseInt(contest)}
            ></ContestInfo> : <>
                <Segment>
                    {currProblem === null ?
                        <Message error>
                            <Message.Header>错误</Message.Header>
                            <Message.Content>
                                非法题目ID: {problem}
                            </Message.Content>
                        </Message>
                        : <>
                            {currProblem.problemType === "selection" ? <SelectionProblem
                                contestID={parseInt(contest)}
                                problemCount={data.problems.length}
                                problem={currProblem}
                                problemID={numberProblem}
                                answers={answers[numberProblem] as string[][]} updateAnswers={ans => setAnswers(old => _.set([...old], numberProblem, ans))}
                            ></SelectionProblem> : <FillBlankProblem
                                contestID={parseInt(contest)}
                                problemCount={data.problems.length}
                                problem={currProblem}
                                problemID={numberProblem}
                                answers={answers[numberProblem] as string[]} updateAnswers={ans => setAnswers(old => _.set([...old], numberProblem, ans))}
                            ></FillBlankProblem>}

                            <Button
                                size="small"
                                disabled={numberProblem === 0}
                                onClick={previousProblem}
                                color="red"
                                icon
                                labelPosition="left"
                            >
                                <Icon name="angle left"></Icon>
                                上一题
                            </Button>
                            <Button
                                size="small"
                                disabled={numberProblem === data.problems.length - 1}
                                onClick={nextProblem}
                                color="green"
                                icon
                                labelPosition="right"
                            >
                                <Icon name="angle right"></Icon>
                                下一题
                            </Button>
                        </>}
                    <Message info>
                        <Message.Header>
                            提示
                        </Message.Header>
                        <Message.Content>
                            <p>按左右方向键可以切换题目，按相应字母可以快速进行选择，按回车键可以校验答案</p>
                        </Message.Content>
                    </Message>
                </Segment>

            </>}
        </>}
    </>;
};

export default PreliminaryContest;