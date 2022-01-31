import _ from "lodash";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Button, Divider, Header, Icon, List } from "semantic-ui-react";
import { Markdown } from "../../common/Markdown";
import { PreliminaryProblemOfChoices, PreliminaryQuestionOfChoices } from "./client/types";

interface SelectionProblemProps {
    contestID: number;
    problemCount: number;
    problem: PreliminaryProblemOfChoices;
    problemID: number;
    answers: string[][];
    updateAnswers: (ans: string[][]) => void;
};

function validateAnswer(valid: string[], user: string[]): boolean {
    if (valid.length !== user.length) return false;
    const userSet = new Set(user);
    for (const chr of valid) {
        if (!userSet.has(chr)) return false;
    }
    return true;
}

function letterOf(index: number): string {
    return String.fromCharCode("A".charCodeAt(0) + index);
}
const SelectionQuestion: React.FC<{
    question: PreliminaryQuestionOfChoices;
    userAnswers: string[];
    onChangeAnswer: (ans: string[]) => void;
    showAnswer: boolean;
}> = ({
    userAnswers,
    onChangeAnswer,
    question,
    showAnswer,
}) => {
        const userAnswerSet = useMemo(() => new Set(userAnswers), [userAnswers]);
        const allowMultiple = question.answers.length > 1;
        const switchAnswer = (c: string) => {
            if (userAnswerSet.has(c)) {
                onChangeAnswer(userAnswers.filter(t => t !== c))
            } else {
                if (allowMultiple) {
                    onChangeAnswer([...userAnswers, c]);
                } else {
                    onChangeAnswer([c]);
                }
            }
        };
        return <>
            <p>{allowMultiple ? "多项选择题" : "单项选择题"} ({question.score} 分)</p>
            {showAnswer && <>
                {validateAnswer(question.answers, userAnswers) ? <div style={{ color: "green" }}>
                    答案正确
                </div> : <div style={{ color: "red" }}>
                    答案错误! 正确答案为: {question.answers.join(" ")}
                </div>}
            </>}
            <List >
                {question.choices.map((choice, i) => <List.Item key={i}>
                    <div className="ui checkbox">
                        <input type="checkbox" checked={userAnswerSet.has(letterOf(i))} onChange={() => switchAnswer(letterOf(i))}></input>
                        <label>
                            <Markdown markdown={`${letterOf(i)}. ${choice}`}></Markdown>
                        </label>
                    </div>
                </List.Item>)}
            </List>
        </>;
    }

const SelectionProblem: React.FC<SelectionProblemProps> = ({
    // contestID,
    // problemCount,
    problem,
    problemID,
    answers,
    updateAnswers
}) => {

    const [showAnswer, setShowAnswer] = useState(false);
    const keyDownHandler = useCallback((evt: KeyboardEvent) => {
        const charCode = evt.key.charCodeAt(0);
        if (evt.key.length === 1 && charCode >= "a".charCodeAt(0) && charCode <= "z".charCodeAt(0)) {
            const diff = charCode - "a".charCodeAt(0);
            let i = 0;
            for (; i < answers.length && answers[i].length > 0; i++);
            if (i < problem.questions.length && diff < problem.questions[i].choices.length) {
                updateAnswers(_.set([...answers], i, [String.fromCharCode(diff + "A".charCodeAt(0))]));
            }
        } else if (evt.key === "Enter") {
            setShowAnswer(true);
        }
    }, [answers, problem.questions, updateAnswers]);
    useEffect(() => {
        window.addEventListener("keydown", keyDownHandler);
        return () => window.removeEventListener("keydown", keyDownHandler);
    }, [keyDownHandler]);
    useEffect(() => {
        setShowAnswer(false);
    }, [problemID]);
    return <>
        <Header as="h3">
            第 {problemID + 1} 题 (共 {problem.score} 分)
        </Header>
        {problem.content && <>
            <Markdown
                markdown={problem.content}
            ></Markdown>
            <Divider></Divider>
        </>}
        {problem.questions.map((question, i) => <div key={i}>
            <SelectionQuestion
                showAnswer={showAnswer}
                question={question}
                userAnswers={answers[i]}
                onChangeAnswer={function (ans: string[]): void {
                    updateAnswers((() => {
                        const t = [...answers];
                        t[i] = ans;
                        return t;
                    })());
                }}
            ></SelectionQuestion>
            <Divider></Divider>
        </div>)}
        <Button size="small" color="blue" icon labelPosition="left" onClick={() => setShowAnswer(true)}>
            <Icon name="checkmark"></Icon>
            校验答案
        </Button>
    </>;
};

export default SelectionProblem;