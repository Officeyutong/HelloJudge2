import GeneralClient from "../../../common/GeneralClient";
import { SolutionListEntry } from "./types";

class ProblemSolutionClient extends GeneralClient {
    async userSubmitSolution(content: string, problem_id: number) {
        await this.client!.post("/api/solution/submit", { content: content, problem_id: problem_id });
    }
    async getProblemSolutionList(problem_id: number, page: number): Promise<{ pageCount: number; data: SolutionListEntry[] }> {
        return (await this.client!.post("/api/solution/problem/list")).data;
    }
    async adminCreateSolution(content: string, top: boolean, problem_id: number) {
        await this.client!.post("/api/solution/admin/submit", { content: content, top: top, problem_id: problem_id });
    }
    async adminVerifySolution(solution_id: number, comment: string) {
        await this.client!.post("/api/solution/admin/verify", { solution_id: solution_id, comment: comment });
    }
    async adminToggleSolutionTopStatus(solution_id: number) {
        await this.client!.post("/api/solution/admin/toggle_top_status", { solution_id: solution_id });
    }
};

const problemSolutionClient = new ProblemSolutionClient();

export default problemSolutionClient;
