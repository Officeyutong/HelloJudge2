import { GeneralUserEntry } from "../../../common/types";

interface SolutionListEntry {
    id: number;
    uploader: GeneralUserEntry;
    content: string;
    top: boolean;
    verified: boolean;
    upload_timestamp: number;
    verifier: GeneralUserEntry;
    verify_timestamp: number;
};
export type {
    SolutionListEntry
}