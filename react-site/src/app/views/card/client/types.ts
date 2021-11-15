import { SubmissionStatus } from "../../../common/types";

interface ProblemCardResponse {
    id: number;
    title: string;
    acceptedCount: number;
    submitCount: number;
    myStatus: null | {
        score: number;
        fullScore: number;
        status: SubmissionStatus;
        submissionID: number;
    }
};

export type {
    ProblemCardResponse
}