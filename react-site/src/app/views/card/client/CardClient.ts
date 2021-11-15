import GeneralClient from "../../../common/GeneralClient";
import { ProblemCardResponse } from "./types";

class CardClient extends GeneralClient {
    async getProblemCard(problemID: number): Promise<ProblemCardResponse> {
        return (await this.client!.post("/api/card/problem", { problemID })).data;
    }
};

const cardClient = new CardClient();


export default cardClient;