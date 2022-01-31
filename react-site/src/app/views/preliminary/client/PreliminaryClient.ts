import GeneralClient from "../../../common/GeneralClient";
import { PreliminaryContestDetail, PreliminaryContestListEntry } from "./types";

class PreliminaryClient extends GeneralClient {
    async getContestList(page: number = 1): Promise<{ pageCount: number; data: PreliminaryContestListEntry[] }> {
        return (await this.unwrapExtraClient!.post("/api/preliminary/contest/list", { page })).data;
    }
    async getContestDetail(id: number): Promise<PreliminaryContestDetail> {
        return (await this.client!.post("/api/preliminary/contest/detail", { id })).data;
    }
};

const preliminaryClient = new PreliminaryClient();

export default preliminaryClient;