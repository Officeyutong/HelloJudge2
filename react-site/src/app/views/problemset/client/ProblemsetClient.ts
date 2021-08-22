import GeneralClient from "../../../common/GeneralClient";
import { ProblemsetEditInfo, ProblemsetListItem, ProblemsetPublicInfo, ProblemsetUpdateInfo } from "./types";

class ProblemsetClient extends GeneralClient {
    async getProblemSetList(page: number): Promise<{ data: ProblemsetListItem[]; pageCount: number }> {
        const resp = (await this.client!.post("/api/problemset/list", { page: page })).data as { items: ProblemsetListItem[]; pageCount: number };
        return {
            data: resp.items,
            pageCount: resp.pageCount
        };
    }
    async createProblemset(): Promise<number> {
        const resp = await this.client!.post("/api/problemset/create");
        return resp.data.id;
    }
    async removeProblemset(id: number) {
        await this.client!.post("/api/problemset/remove", { id: id });
    }
    async getProblemsetEditInfo(id: number): Promise<ProblemsetEditInfo> {
        return (await this.client!.post("/api/problemset/get", { id: id })).data;
    }
    async updateProblemset(data: ProblemsetUpdateInfo) {
        await this.client!.post("/api/problemset/update", { data: data });
    }
    async unlockProblemset(id: number, code: string) {
        await this.client!.post("/api/problemset/join_private_problemset", { id: id, code: code });
    }
    async getProblemsetFrontendInfo(id: number): Promise<ProblemsetPublicInfo> {
        return (await this.client!.post("/api/problemset/get_public", { id: id })).data;
    }
    
};

const problemsetClient = new ProblemsetClient();

export default problemsetClient;