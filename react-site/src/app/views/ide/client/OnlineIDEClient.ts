import QueryString from "qs";
import GeneralClient from "../../../common/GeneralClient";
import { IDERunResponse } from "./types";

class OnlineIDEClient extends GeneralClient {
    async submit(code: string, input: string, lang: string, parameter: string): Promise<{ run_id: string }> {
        return (await this.client!.post("/api/ide/submit", QueryString.stringify({
            code: code, input: input, lang: lang, parameter: parameter
        }))).data;
    }
    async fetchStatus(run_id: string): Promise<IDERunResponse> {
        return (await this.client!.post("/api/ide/fetch_status", { run_id: run_id })).data;
    }
};

const onlineIDEClient = new OnlineIDEClient();

export default onlineIDEClient;