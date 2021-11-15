interface ChallengeListEntry {
    id: number;
    name: string;
    description: string;
    problemsetList: number[];
    accessible: boolean;
    level: number;
    hasFinished: boolean;
};

interface ChallengeRawData {
    id: number;
    name: string;
    level: number;
    description: string;
    problemsetList: number[];
};

interface ChallengeDetail {
    name: string;
    id: number;
    description: string;
    level: number;
    hasFinished: boolean;
    accessible: boolean;
    problemsetList: {
        name: string;
        hasFinished: boolean;
        id: number;
    }[];
};

export type {
    ChallengeDetail,
    ChallengeListEntry,
    ChallengeRawData,
}