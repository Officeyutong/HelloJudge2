type IDERunStatus = "done" | "running";

interface IDERunResponse {
    run_id: string;
    message: string;
    status: IDERunStatus;
};

interface IDERunStoredData {
    code: string;
    input: string;
    lang: string;
    parameter: string;
};

export type {
    IDERunResponse,
    IDERunStatus,
    IDERunStoredData
}