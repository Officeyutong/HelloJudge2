import { GeneralUserEntry } from "../../../common/types";

interface WikiNavigationListItem {
    title: string;
    target: number;
    children: {
        title: string;
        target: number;
    }[];
};
interface WikiConfig {
    indexPage: string;
};
interface NavigationEntry<MenuAsString extends boolean> {
    id: number;
    title: string;
    // 以文本形式提供的 WikiNavigationItem[]
    menu: MenuAsString extends true ? string : WikiNavigationListItem[];
    priority: number;
};

interface GetWikiConfigResponse<MenuAsText extends boolean> {
    config: WikiConfig;
    navigations: NavigationEntry<MenuAsText>[];
};
interface WikiPageDetail {
    comment: string;
    pageID: number;
    content: string;
    title: string;
    version: number;
    user: GeneralUserEntry;
    time: number;
    verified: boolean;
    menu: WikiNavigationListItem[];
    navigationID: number;

};

// type WikiPageDetail<editing extends boolean> = editing extends true ? (WikiPageDetailBase & {
//     basedOn: {
//         version: number;
//         user: {
//             uid: number;
//             username: string;
//         }
//         time: number;
//         verified: boolean;
//     }
// }) : WikiPageDetailBase;


interface WikiVersionListItem {
    id: number;
    title: string;
    time: number;
    user: {
        uid: number;
        username: string;
    };
    verified: number;
    nagivationID: number;
    base: number;
    comment: string;
};


export type {
    GetWikiConfigResponse,
    NavigationEntry,
    WikiConfig,
    WikiNavigationListItem,
    WikiPageDetail,
    // WikiPageDetailBase,
    WikiVersionListItem,
}