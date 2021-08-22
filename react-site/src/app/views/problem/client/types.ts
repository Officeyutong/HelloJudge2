import { ProblemTagEntry, ProgrammingLanguageEntry, SubmissionStatus } from "../../../common/types";

interface ProblemFileEntry {
    last_modified_time?: number;//浮点数，时间戳
    name: string;
    size: number;
}
interface ExampleEntry { input: string; output: string; };
interface TestcaseEntry {
    input: string;
    output: string;
    full_score: number;
}
type SubtaskScoringMethod = "min" | "sum";
interface SubtaskEntry {
    name: string;
    score: number;
    method: SubtaskScoringMethod;
    testcases: TestcaseEntry[];
    time_limit: number;//时间限制，毫秒
    memory_limit: number;//内存限制，MB
    comment: string;
};
interface ExtraParameterEntry {
    lang: string;
    parameter: string;
    name: string;
    force: boolean;
};
interface ProblemEditStatement {
    title: string;
    background: string;
    content: string;
    input_format: string;
    output_format: string;
    hint: string;
    example: ExampleEntry[];
};
interface ProblemStatement extends ProblemEditStatement {
    id: number;
    subtasks: SubtaskEntry[];
};

type ProblemType = "traditional" | "remote_judge" | "submit_answer";

interface ProblemInfo extends ProblemStatement {
    managable: boolean;
    id: number;
    files: ProblemFileEntry[];
    last_code: string;
    last_lang: string;
    accepted_count: number;//通过数
    submission_count: number;//提交数
    my_submission: -1 | number;//-1表示没提交过
    my_submission_status: SubmissionStatus;
    score: number;
    extra_parameter: ExtraParameterEntry[];
    uploader: {
        uid: number; username: string;
    };
    recentDiscussions: { title: string; id: number }[];
    languages: ProgrammingLanguageEntry[];
    tags: ProblemTagEntry[];
    hasPermission: boolean; //是否有权限查看该题
    inTodoList: boolean;
    submissionVisible: boolean;
    problem_type: ProblemType;
    public: boolean;
    can_see_results: boolean;
    create_time: string;
    spj_filename: string;
    remote_judge_oj: string;
    using_file_io: boolean;
    remote_problem_id: string;
    uploader_id: number;
    input_file_name: string;
    output_file_name: string;
    downloads: string[];
    provides: string[];

    lastUsedParameters: number[];
};
interface ProblemUpdateInfo extends ProblemStatement {
    extra_parameter: ExtraParameterEntry[];
    can_see_results: boolean;
    public: boolean;
    spj_filename: string;
    using_file_io: boolean;
    input_file_name: string;
    output_file_name: string;
    downloads: string[];
    provides: string[];
    invite_code: string;
    submissionVisible: boolean;
    newProblemID: number;
};

interface ProblemEditReceiveInfo extends ProblemInfo {
    invite_code: string; //编辑模式时存在
}

interface ProblemSearchFilter {
    searchKeyword?: string;
    tag?: string[]
}
interface ProblemListEntry {
    id: number;
    title: string;
    mySubmission: { id: number; status: string; };
    public: boolean;
    totalSubmit: number;
    acceptedSubmit: number;
    tags: string[];
};

const ScoringMethodMapping: { [K in SubtaskEntry["method"]]: string } = {
    min: "取最小值(捆绑测试)",
    sum: "取和(分数相加)"
};

export type {
    ProblemFileEntry,
    ProblemInfo,
    ExampleEntry,
    ExtraParameterEntry,
    ProblemUpdateInfo,
    ProblemListEntry,
    ProblemSearchFilter,
    ProblemStatement,
    ProblemEditStatement,
    ProblemEditReceiveInfo,
    SubtaskEntry,
    SubtaskScoringMethod,
    ProblemType
}

export {
    ScoringMethodMapping
}