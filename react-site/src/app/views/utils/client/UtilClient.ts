import GeneralClient from "../../../common/GeneralClient";
import { ProgrammingLanguageEntry } from "../../../common/types";

class UtilClient extends GeneralClient {
    async recaptchaPreparation(): Promise<{ site_key: string }> {
        return (await this.client!.post("/api/phoneutil/preparation")).data;
    }
    async sendSMSCode(phone: string, client_response: any, must_not_use: boolean): Promise<{ code: number; message: string }> {
        return (await this.unwrapClient!.post("/api/phoneutil/sendcode", { phone: phone, client_response: client_response, must_not_use: must_not_use })).data;
    }
    async getSupportedLanguages(): Promise<ProgrammingLanguageEntry[]> {
        const resp = await (await this.client!.post("/api/get_supported_langs")).data;
        return resp;
    }
};

const utilClient = new UtilClient();

export default utilClient;