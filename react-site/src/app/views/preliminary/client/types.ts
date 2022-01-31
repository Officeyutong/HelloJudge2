interface PreliminaryContestListEntry {
    title: string;
    id: number;
    duration: number;
};

interface PreliminaryQuestionBase {
    score: number;
};
interface PreliminaryQuestionOfChoices extends PreliminaryQuestionBase {
    choices: string[];
    answers: string[];
};
interface PreliminaryQuestionOfBlanks extends PreliminaryQuestionBase {
    answers: string[];
    multiline: boolean;
};

interface PreliminaryProblemBase {
    problemID: number;
    content: string;
    score: number;
    problemType: "selection" | "fill_blank";
};

interface PreliminaryProblemOfChoices extends PreliminaryProblemBase {
    problemType: "selection";
    questions: PreliminaryQuestionOfChoices[];
};
interface PreliminaryProblemOfBlanks extends PreliminaryProblemBase {
    problemType: "fill_blank";
    questions: PreliminaryQuestionOfBlanks[];
};

interface PreliminaryContestDetail {
    title: string;
    duration: number;
    description: string;
    uploader: {
        uid: number;
        username: string;
    }
    upload_time: number;
    problems: (PreliminaryProblemOfChoices | PreliminaryProblemOfBlanks)[];
};

export type {
    PreliminaryContestListEntry,
    PreliminaryProblemBase,
    PreliminaryProblemOfBlanks,
    PreliminaryProblemOfChoices,
    PreliminaryQuestionBase,
    PreliminaryQuestionOfBlanks,
    PreliminaryQuestionOfChoices,
    PreliminaryContestDetail
}