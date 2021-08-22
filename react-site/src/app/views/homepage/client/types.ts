import { SemanticCOLORS } from "semantic-ui-react/dist/commonjs/generic";

interface FriendLinkEntry {
    name: string;
    url: string;
};
interface ToolBoxEntry {
    name: string;
    url: string;
    color: SemanticCOLORS;
};
interface HomePageData {
    appName: string;
    friendLinks: FriendLinkEntry[];
    toolbox: ToolBoxEntry[];
};

export type {
    FriendLinkEntry,
    ToolBoxEntry,
    HomePageData
}