import { GeneralUserEntry, SubmissionStatus } from "../../../common/types";
import { ExtraParameterEntry, ProblemFileEntry, ProblemStatement, ProblemType } from "../../problem/client/types";

interface ContestRanklist {
    closed: boolean;
    running: boolean;
    refresh_interval: number;
    name: string;
    contest_id: number;
    using_penalty: boolean;
    managable: boolean;
    ranklist: {
        rank: number;
        uid: number;
        username: string;
        virtual: boolean;
        virtualContestID: number | -1;
        scores: {
            score: number;
            submit_count: number; //提交数
            ac_time: number; //通过分钟数，-1表示未通过
            penalty: number; //本题罚时
            submit_id: number | -1;
            status: SubmissionStatus;
            first_blood: boolean;
            submit_time: number;

        }[];
        total: {
            score: number; //总分
            penalty: number; //总罚时 
            ac_count: number; //AC数
            submit_time_sum: number; //AC题目的总提交时间和
        }
    }[];
    problems: {
        name: string;
        id: number; //比赛里的题目ID
        accepted_submit: number;
        total_submit: number;
    }[];
};

interface ClarificationDetailResponse {
    sender: GeneralUserEntry;
    send_time: string;
    content: string;
    replied: string;
    replier: GeneralUserEntry;
    reply_time: string;
    reply_content: string;
    id: number;
};
interface ClarificationListResponse {
    pageCount: number;
    data: ClarificationDetailResponse[];
}
interface ContestListEntry {
    id: number;
    name: string;
    owner_id: number;
    owner_username: string;
    start_time: number;// second
    end_time: number;// second
    privateContest: boolean;
    hasPermission: boolean;
};
interface ContestListResponse {
    page_count: number;
    list: ContestListEntry[];
};
type RankCriterion = "max_score" | "last_submit" | "penalty";
const RankCriterionMapping: { [K in RankCriterion]: string } = {
    last_submit: "最后一次提交",
    max_score: "最高分数提交",
    penalty: "过题数与罚时"
};
interface ContestShowProblemResponse {
    weight: number;
    title: string;
    id: number; //problem id in contest
    total_submit: number | -1;// total submit count, -1: invisible
    accepted_submit: number | -1;
    my_submit: number;
    status: SubmissionStatus;
    rawID: number;
};
interface ContestShowDetailResponse {
    managable: boolean;
    name: string;
    description: string;
    id: number;
    owner_id: number;
    owner_username: string;
    start_time: number; //seconds;
    end_time: number;
    ranklist_visible: boolean;
    judge_result_visible: boolean;
    rank_criterion: RankCriterion;
    private_contest: boolean;
    problems: ContestShowProblemResponse[];
    accessible: boolean;
    closed: boolean;
    virtual: boolean;
    hasPermission: boolean; //是否有权访问
};
interface ContestEditProblem {
    id: number; weight: number;
};
interface ContestEditRawDataResponse {
    id: number;
    name: string;
    description: string;
    start_time: number;// seconds
    end_time: number;
    problems: ContestEditProblem[];
    ranklist_visible: boolean;
    judge_result_visible: boolean;
    rank_criterion: RankCriterion;
    private_contest: boolean;
    invite_code: string;
    closed: boolean;
};
interface ContestDetailUpdateRequest {
    name: string;
    start_time: number;// in seconds
    end_time: number;
    problems: ContestEditProblem[];
    ranklist_visible: boolean;
    judge_result_visible: boolean;
    rank_criterion: RankCriterion;
    private_contest: boolean;
    invite_code: string;
    description: string;
};

interface ContestProblemShow extends ProblemStatement {
    files: ProblemFileEntry[];
    score: number;
    extra_parameter: ExtraParameterEntry[];
    virtual: boolean;
    downloads: string[];
    using_file_io: boolean;
    input_file_name: string;
    output_file_name: string;
    problem_type: ProblemType;
    last_code: string;
    last_lang: string;
    usedParameters: number[];
}
type ContestSortingOrder = "id" | "start_time";
const ContestSortingOrderMapping: { [K in ContestSortingOrder]: string } = {
    id: "比赛ID",
    start_time: "开始时间"
}
export type {
    ContestRanklist,
    ClarificationDetailResponse,
    RankCriterion,
    ClarificationListResponse,
    ContestListEntry,
    ContestListResponse,
    ContestShowDetailResponse,
    ContestShowProblemResponse,
    ContestEditRawDataResponse,
    ContestEditProblem,
    ContestDetailUpdateRequest,
    ContestProblemShow,
    ContestSortingOrder
};

export {
    ContestSortingOrderMapping,
    RankCriterionMapping
}