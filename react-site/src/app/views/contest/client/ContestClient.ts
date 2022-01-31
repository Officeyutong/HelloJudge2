import GeneralClient from "../../../common/GeneralClient";
import { APIError } from "../../../Exception";
import { ClarificationDetailResponse, ClarificationListResponse, ContestDetailUpdateRequest, ContestEditRawDataResponse, ContestListResponse, ContestProblemShow, ContestRanklist, ContestShowDetailResponse, ContestSortingOrder } from "./types";

class ContestClient extends GeneralClient {
    async getContestRanklist(contestID: number, virtualID: number): Promise<ContestRanklist> {
        return (await this.client!.post("/api/contest/ranklist", {
            contestID: contestID,
            virtualID: virtualID
        })).data as ContestRanklist;
    };
    async getContestClarificationDetail(clarification_id: number): Promise<ClarificationDetailResponse> {
        return (await this.client!.post("/api/contest/clarification/detail", { clarification_id })).data;
    }
    async removeClarification(clarification_id: number) {
        await this.client!.post("/api/contest/clarification/remove", { clarification_id });
    }
    async replyClarification(clarification_id: number, content: string) {
        await this.client!.post("/api/contest/clarification/reply", { clarification_id, content });
    }
    async sendClarification(contest: number, content: string) {
        await this.client!.post("/api/contest/clarification/send", { contest, content });
    }
    async getClarificationList(contest: number, page: number = 1): Promise<ClarificationListResponse> {
        const resp = (await (this.unwrapClient!.post("/api/contest/clarification/all", { contest, page }))).data as (ClarificationListResponse & { code: number; message: string });
        if (resp.code !== 0) {
            throw new APIError(resp.message);
        }
        return resp;
    }
    async closeContest(contestID: number) {
        await this.client!.post("/api/contest/close", { contestID });
    }
    async unlockContest(contestID: number, inviteCode: string) {
        await this.client!.post("/api/contest/unlock", { contestID, inviteCode });
    }
    async removeContest(contestID: number) {
        await this.client!.post("/api/contest/remove", { contestID });
    }
    async createContest(): Promise<{ contest_id: number }> {
        const resp = (await this.unwrapClient!.post("/api/contest/create")).data as { code: number; message: string; contest_id: number };
        if (resp.code !== 0) {
            throw new APIError(resp.message);
        }
        return resp;
    }
    async getContestList(page: number = 1, order_by: ContestSortingOrder = "start_time"): Promise<ContestListResponse> {
        return (await (this.client!.post("/api/contest/list", { page, order_by }))).data;
    }
    async getContestDetail(contestID: number, virtualID: number): Promise<ContestShowDetailResponse> {
        return (await (this.client!.post("/api/contest/show", { contestID, virtualID }))).data;
    }
    async getContestRawData(contestID: number): Promise<ContestEditRawDataResponse> {
        return (await this.client!.post("/api/contest/raw_data", { contestID })).data;
    }
    async updateContest(contestID: number, data: ContestDetailUpdateRequest) {
        await this.client!.post("/api/contest/update", { contestID, data });
    }
    makeFileDownloadUrl(contest: number, problem: number, filename: string) {
        return `/api/contest/${contest}/${problem}/download_file/${filename}`;
    }
    async getContestProblemDetail(problemID: number, contestID: number, virtualID: number): Promise<ContestProblemShow> {
        return (await this.client!.post("/api/contest/problem/show", { problemID, contestID, virtualID })).data;
    }
    async refreshRanklist(contestID: number, virtualID: number) {
        await this.client!.post("/api/contest/refresh_ranklist", { contestID, virtualID });
    }
};


const contestClient = new ContestClient();

export default contestClient;
