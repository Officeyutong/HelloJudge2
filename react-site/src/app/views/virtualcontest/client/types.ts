interface VirtualContestEntry {
    contest: {
        id: number;
        name: string;
    };
    startTime: number;
    endTime: number;
    id: number;
};

export type {
    VirtualContestEntry
}