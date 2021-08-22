import GeneralClient from "../../../common/GeneralClient";
import { VirtualContestEntry } from "./types";

class VirtualContestClient extends GeneralClient {

    async createVirtualContest(contestID: number, startAt: number): Promise<{ id: number }> {
        return (await this.client!.post("/api/virtualcontest/create", { contestID, startAt })).data;
    }
    async getVirtualContestList(page: number): Promise<{ pageCount: number; data: VirtualContestEntry[] }> {
        return (await this.unwrapExtraClient!.post("/api/virtualcontest/list", { page })).data;
    }
};

const virtualContestClient = new VirtualContestClient();

export default virtualContestClient;