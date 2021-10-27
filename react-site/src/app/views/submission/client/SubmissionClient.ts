import QueryString from "qs";
import GeneralClient from "../../../common/GeneralClient";
import { SubmissionFilter, SubmissionInfo, SubmissionListEntry } from "./types";

class SubmissionClient extends GeneralClient {
    async rejudge(submission_id: number) {
        await this.client!.post("/api/rejudge", QueryString.stringify({ submission_id }));
    }
    async getSubmissionInfo(submission_id: number): Promise<SubmissionInfo> {
        return (await this.client!.post("/api/get_submission_info", QueryString.stringify({ submission_id }))).data;
    }
    async getSubmissionList(page: number, filter: SubmissionFilter): Promise<{
        page_count: number;
        data: SubmissionListEntry[];
    }> {
        const resp = (await this.unwrapExtraClient!.post("/api/submission_list", {
            page, filter
        })).data;

        return resp;
    }
};

const submissionClient = new SubmissionClient();

export default submissionClient;