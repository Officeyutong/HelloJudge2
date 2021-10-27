import { SubmissionStatus } from "../../../common/types";

interface ProblemtodoEntry {
    id: number;
    title: string;
    joinTime: string;
    submission: {
        id: number;
        status: SubmissionStatus;
    }
};

export type {
    ProblemtodoEntry
};