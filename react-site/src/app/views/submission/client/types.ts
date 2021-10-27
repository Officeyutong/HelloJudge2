import { Schema } from "jsonschema";
import { SubmissionStatus } from "../../../common/types";
import { ProblemInfo } from "../../problem/client/types";

interface TestcaseJudgeResult {
    input: string;
    output: string;
    score: number;
    status: SubmissionStatus;
    message: string;
    time_cost: number;
    memory_cost: number;
    full_score: number;
};

interface SubtaskJudgeResult {
    score: number;
    status: SubmissionStatus;
    testcases: TestcaseJudgeResult[];
};

interface SubmissionInfo {
    usePolling: boolean;
    managable: boolean;
    id: number;
    language: string;
    language_name: string;
    submit_time: string;
    public: boolean;
    contest: {
        id: number;
        name: string;
        isContest: boolean;
    };
    code: string;
    judge_result: { [x: string]: SubtaskJudgeResult };
    status: SubmissionStatus;
    message: string;
    judger: string;
    score: number;
    ace_mode: string;
    hljs_mode: string;
    time_cost: number;
    memory_cost: number;
    extra_compile_parameter: string;
    isRemoteSubmission: boolean;
    problem: {
        id: number;
        title: string;
        rawID: number;
        score: number;
        subtasks: ProblemInfo["subtasks"];
    };
    user: {
        uid: number;
        username: string;
    }
    virtualContestID: number;
};

interface SubmissionFilter {
    uid?: string;
    status?: "accepted" | "unaccepted" | "judging" | "waiting" | "compile_error";
    min_score?: number;
    max_score?: number;
    problem?: number;
    contest?: number;
};

const SubmissionFilterSchema: Schema = {
    type: "object",
    properties: {
        uid: {
            type: "string"
        },
        status: {
            type: "string",
            enum: ["accepted", "unaccepted", "judging", "waiting", "compile_error"]
        },
        min_score: {
            type: "number",
            minimum: 0
        },
        max_score: {
            type: "number",
            minimum: 0
        },
        problem: {
            type: "number"
        },
        contest: {
            type: "number"
        }
    }
};

interface SubmissionListEntry {
    id: number;
    status: SubmissionStatus;
    score: number;
    contest: number | -1;
    uid: number;
    username: string;
    submit_time: string;
    memory_cost: number;
    time_cost: number;
    problem_id: number;
    problem_title: number;
    total_score: number;
};

export type {
    SubmissionInfo,
    SubmissionFilter,
    TestcaseJudgeResult,
    SubtaskJudgeResult,
    SubmissionListEntry
};

export {
    SubmissionFilterSchema
}