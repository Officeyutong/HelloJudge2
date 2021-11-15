import GeneralClient from "../../../common/GeneralClient";

class MiscClient extends GeneralClient {
    async getHelpDoc(): Promise<string> {
        return (await (this.unwrapClient!.get("/api/get_help_markdown"))).data;
    };
}

const miscClient = new MiscClient();
export default miscClient;