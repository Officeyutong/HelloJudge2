import GeneralClient from "../../../common/GeneralClient";
import { HomePageData } from "./types";

class HomePageClient extends GeneralClient {
    async loadData(): Promise<HomePageData> {
        return (await this.client!.post("/api/home_page")).data;
    };
}

const homepageClient = new HomePageClient();

export default homepageClient;