import GeneralClient from "../../../common/GeneralClient";
import { ProblemtodoEntry } from "./types";

class ProblemtodoClient extends GeneralClient {
    async add(problemID: number) {
        await this.client!.post("/api/problemtodo/add", { problemID: problemID });
    }
    async remove(problemID: number) {
        await this.client!.post("/api/problemtodo/remove", { problemID: problemID });
    }
    async getAll(): Promise<ProblemtodoEntry[]> {
        return (await this.client!.post("/api/problemtodo/all")).data;
    }
};

const problemtodoClient = new ProblemtodoClient();

export default problemtodoClient;
