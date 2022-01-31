import GeneralClient from "../../../common/GeneralClient";
import { GetWikiConfigResponse, NavigationEntry, WikiConfig, WikiPageDetail, WikiVersionListItem } from "./types";

class WikiClient extends GeneralClient {
    async createNavigationItem(): Promise<NavigationEntry<true>> {
        return (await this.client!.post("/api/wiki/config/navigation/create")).data;
    }
    async updateWikiConfig(
        config: WikiConfig,
        navigations: NavigationEntry<true>
    ) {
        await this.client!.post("/api/wiki/config/update", { config, navigations });
    }
    async getWikiConfig(menuAsText: boolean): Promise<GetWikiConfigResponse<true> | GetWikiConfigResponse<false>> {
        return (await this.client!.post("/api/wiki/config/get", { menu_as_text: menuAsText })).data;
    }
    async getWikiPageDetails(page: number, version: number, editing: boolean): Promise<WikiPageDetail> {
        return (await this.client!.post("/api/wiki/page", { page, version, editing })).data;
    }
    async createNewVersion(page: number, version: number, content: string, navigation_id: number, comment: string) {
        await this.client!.post("/api/wiki/newversion", {
            page, version, content, navigation_id, comment
        });
    }
    async createNewPage(title: string, content: string, navigation_id: number): Promise<{ pageID: number }> {
        const resp = (await this.unwrapExtraClient!.post("/api/wiki/createpage", { title, content, navigation_id })).data;
        return { pageID: resp.pageID };
    }
    async verifyVersion(version: number): Promise<{ id: number }> {
        const resp = (await this.unwrapExtraClient!.post("/api/wiki/verify", { version })).data as { id: number };
        return { id: resp.id };
    }
    async getVersionList(pageID: number, page: number): Promise<{ pageCount: number; data: WikiVersionListItem[] }> {
        return (await this.unwrapExtraClient!.post("/api/wiki/versions", { pageID, page })).data;
    }
}

const wikiClient = new WikiClient();

export default wikiClient;
