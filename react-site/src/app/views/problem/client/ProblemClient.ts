import GeneralClient from "../../../common/GeneralClient";
import qs from "qs";
import { ProblemEditReceiveInfo, ProblemFileEntry, ProblemInfo, ProblemListEntry, ProblemSearchFilter, ProblemUpdateInfo } from "./types";
import { ProblemTagEntry } from "../../../common/types";
import { APIError } from "../../../Exception";
class ProblemClient extends GeneralClient {
    async unlockProblem(problemID: string, inviteCode: string) {
        await this.client!.post("/api/problem/unlock", { problemID: problemID, inviteCode: inviteCode });
    }
    async removeProblem(problem_id: number) {
        await this.client!.post("/api/problem/remove", qs.stringify({ problem_id: problem_id }));
    }
    async refreshCachedCount(problem_id: number) {
        await this.client!.post("/api/refresh_cached_count", { problem_id: problem_id });
    }
    async regenerateFileList(problem_id: number): Promise<ProblemFileEntry[]> {
        return (await this.client!.post("/api/regenerate_filelist", qs.stringify({ problem_id: problem_id }))).data;
    }
    async getProblemInfo(id: number, edit: true): Promise<ProblemEditReceiveInfo>;
    async getProblemInfo(id: number, edit: false): Promise<ProblemInfo>;
    async getProblemInfo(id: number, edit: boolean): Promise<any> {
        return (await this.client!.post("/api/get_problem_info", qs.stringify({ id: id, edit: edit ? 1 : 0 }))).data;
    }
    async updateProblemInfo(
        id: number,
        data: ProblemUpdateInfo,
        submitAnswer: boolean) {
        await this.client!.post("/api/update_problem", qs.stringify({ id: id, data: JSON.stringify(data), submitAnswer: submitAnswer ? "true" : "false" }));
    }
    async uploadProblemFile(id: number, files: FormData, prorgressHandler: (evt: ProgressEvent) => void): Promise<{ file_list: ProblemFileEntry[]; message?: string }> {
        return (await this.unwrapClient!.post(`/api/upload_file/${id}`, files, { headers: { 'Content-Type': 'multipart/form-data' }, onUploadProgress: prorgressHandler })).data;
    }
    async removeProblemFile(id: number, file: string): Promise<{ file_list: ProblemFileEntry[]; }> {
        return (await this.unwrapClient!.post("/api/remove_file", qs.stringify({ id: id, file: file }))).data
    }
    async getProblemList(page: number, filter: ProblemSearchFilter): Promise<{ code: number; pageCount: number; data: ProblemListEntry[]; message: string; }> {
        return (await this.unwrapClient!.post("/api/problem_list", { page: page, filter: filter })).data;
    }
    async createProblem(): Promise<{ problem_id: number }> {
        return (await this.unwrapClient!.post("/api/create_problem")).data;
    }
    async rejudgeAll(problem_id: number) {
        await (await this.client!.post("/api/problem/rejudge_all", { problem_id: problem_id })).data;
    }
    async submit(problemId: number | string, code: string, language: string, usedParameters: number[], contestId: number = -1, virtualID: number | undefined = undefined): Promise<number> {
        const resp = (await this.unwrapClient!.post("/api/submit", qs.stringify({
            problem_id: problemId,
            code: code,
            language: language,
            contest_id: contestId,
            usedParameters: JSON.stringify(usedParameters),
            virtualID: virtualID
        }))).data as { code: number; submission_id: number; };
        return resp.submission_id;
    }
    async submitWithAnswer(
        answerData: Blob,
        problemId: number | string,
        contestId: number = -1,
        virtualID: number | undefined = undefined,
        progressor: (evt: ProgressEvent) => void
    ): Promise<number> {
        const data = new FormData();
        data.append("problem_id", String(problemId));
        data.append("code", "");
        data.append("language", "cpp");
        data.append("contest_id", String(contestId));
        data.append("usedParameters", "[]");
        if (virtualID !== undefined)
            data.append("virtualID", String(virtualID));
        data.append("answerData", answerData);
        return (await this.unwrapExtraClient!.post("/api/submit", data, {
            "headers": { "Content-Type": "multipart/form-data" },
            onUploadProgress: progressor
        })).data.submission_id as number;
    }
    async getProblemtags(): Promise<ProblemTagEntry[]> {
        return (await this.client!.post("/api/problemtag/all")).data;
    }
    async removeProblemTag(id: string) {
        await this.client!.post("/api/problemtag/remove", { id: id });
    }
    async updateProblemTag(id: string, display: string, color: string) {
        await this.client!.post("/api/problemtag/update", { id: id, display: display, color: color });
    }
    async createProblemTag(id: string): Promise<{ display: string; color: string }> {
        const resp: { display: string; color: string; code: number; message: string; } = (await this.unwrapClient!.post("/api/problemtag/create", { id: id })).data;
        if (resp.code !== 0) {
            throw new APIError(resp.message);
        }
        return {
            display: resp.display,
            color: resp.color
        };
    }
    async updateTagsForProblem(problemID: number, tags: string[]) {
        await this.client!.post("/api/problemtag/update_problem", { problemID: problemID, tags: tags });
    }
};

const problemClient = new ProblemClient();

export default problemClient;
