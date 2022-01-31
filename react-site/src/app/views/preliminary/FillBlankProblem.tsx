import _ from "lodash";
import { useCallback, useEffect, useState } from "react";
import { Button, Divider, Form, Icon, Input, TextArea } from "semantic-ui-react";
import { Markdown } from "../../common/Markdown";
import { PreliminaryProblemOfBlanks } from "./client/types";

interface FillBlankProblemProps {
    contestID: number;
    problemCount: number;
    problem: PreliminaryProblemOfBlanks;
    problemID: number;
    answers: string[];
    updateAnswers: (ans: string[]) => void;
};

function validateAnswer(ans: string[], user: string): boolean {
    return ans.includes(user.trim());
}

const FillBlankProblem: React.FC<FillBlankProblemProps> = ({
    problem,
    problemID,
    answers,
    updateAnswers
}) => {
    const [showAnswer, setShowAnswer] = useState(false);
    const keyDownHandler = useCallback((evt: KeyboardEvent) => {
        if (evt.key === "Enter") {
            setShowAnswer(true);
        }
    }, []);
    useEffect(() => {
        window.addEventListener("keydown", keyDownHandler);
        return () => window.removeEventListener("keydown", keyDownHandler);
    }, [keyDownHandler]);
    useEffect(() => {
        setShowAnswer(false);
    }, [problemID]);
    return <>
        <Markdown
            markdown={problem.content}
        ></Markdown>
        <Divider></Divider>
        <Form>
            {problem.questions.map((question, i) => <Form.Field key={i}>
                <label>[填空题 ({question.score} 分)]</label>
                {showAnswer && (validateAnswer(question.answers, answers[i]) ? <div style={{ color: "green" }}>
                    答案正确
                </div> : <div style={{ color: "red" }}>
                    答案错误! 正确答案为: {question.answers.join(" 或 ")}
                </div>)}
                {question.multiline ? <TextArea value={answers[i]} onChange={(e, d) => updateAnswers(_.set([...answers], i, d.value!))}></TextArea>
                    : <Input value={answers[i]} onChange={(e, d) => updateAnswers(_.set([...answers], i, d.value!))}></Input>
                }
                <Divider></Divider>
            </Form.Field>)}

        </Form>
        <Button size="small" color="blue" icon labelPosition="left" onClick={() => setShowAnswer(true)}>
            <Icon name="checkmark"></Icon>
            校验答案
        </Button>
    </>;
};

export default FillBlankProblem;