import { GeneralUserEntry, SubmissionStatus } from "../../../common/types";
type ProblemsetUser = Omit<GeneralUserEntry, "email">;
interface ProblemsetListItem {
    id: number;
    name: string;
    owner: ProblemsetUser;
    problemCount: number;
    private: 0 | 1;
    accessible: boolean;
    createTime: string;
};
interface ForeignProblemEntry {
    name: string;
    url: string;
};
interface ProblemsetUpdateInfo {
    name: string;
    id: number;
    private: 0 | 1;
    invitationCode: string;
    showRanklist: 0 | 1;
    problems: number[];
    description: string;
    foreignProblems: ForeignProblemEntry[];
};
interface ProblemsetEditInfo extends ProblemsetUpdateInfo {
    owner: ProblemsetUser;
    createTime: string;
};
interface ProblemsetPublicInfo {
    owner: ProblemsetUser;
    name: string;
    id: number;
    private: 0 | 1;
    showRanklist: 0 | 1;
    problems: {
        title: string;
        id: number;
        userResult: {
            score: number;
            status: SubmissionStatus;
            submissionID: -1 | number;
        }
    }[];
    createTime: string;
    description: string;
    managable: boolean;
    foreignProblems: ForeignProblemEntry[];
};
export type {
    ProblemsetListItem,
    ForeignProblemEntry,
    ProblemsetEditInfo,
    ProblemsetPublicInfo,
    ProblemsetUpdateInfo,
    ProblemsetUser,
};