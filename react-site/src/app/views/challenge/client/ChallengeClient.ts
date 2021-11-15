import GeneralClient from "../../../common/GeneralClient";
import { ChallengeDetail, ChallengeListEntry, ChallengeRawData } from "./types";

class ChallengeClient extends GeneralClient {
    async getChallengeList(): Promise<{ managable: boolean; data: ChallengeListEntry[] }> {
        return (await this.unwrapExtraClient!.post("/api/challenge/list")).data;
    }
    async unlockChallenge(id: number) {
        await this.client!.post("/api/challenge/unlock", { id });
    }
    async finishProblemset(challengeID: number, problemsetID: number) {
        await this.client!.post("/api/challenge/finish_problemset", { challengeID, problemsetID });
    }
    async getChallengeRawData(id: number): Promise<ChallengeRawData> {
        return (await this.client!.post("/api/challenge/detail_raw", { id })).data;
    }
    async updateChallenge(id: number, name: string, level: number, description: string, problemsetList: number[]) {
        await this.client!.post("/api/challenge/update", { id, name, level, description, problemsetList });
    }
    async removeChallenge(id: number) {
        await this.client!.post("/api/challenge/remove", { id });
    }
    async createChallenge(): Promise<{ id: number }> {
        return (await this.unwrapExtraClient!.post("/api/challenge/create")).data;
    }
    async getChallengeDetail(challengeID: number): Promise<ChallengeDetail> {
        return (await this.client!.post("/api/challenge/detail", { challengeID })).data;
    }
};

const challengeClient = new ChallengeClient();

export default challengeClient;