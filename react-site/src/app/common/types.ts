type SubmissionStatus = string;
type int = number;
type str = string;

interface GeneralUserEntry {
    uid: number;
    username: string;
    email: string;
}
interface SimpleGeneralUserEntry {
    uid: number;
    username: string;
}

interface ProgrammingLanguageEntry {
    id: string;
    display: string;
    version: string;
    ace_mode: string;
    hljs_mode: string;
};
interface ProblemTagEntry {
    id: string;
    display: string;
    color: string;
};
type ButtonClickEvent = React.MouseEvent<HTMLButtonElement, MouseEvent>;
type KeyDownEvent = React.KeyboardEvent<HTMLInputElement>;
export type {
    SubmissionStatus,
    GeneralUserEntry,
    int,
    str,
    ProgrammingLanguageEntry,
    ProblemTagEntry,
    ButtonClickEvent,
    KeyDownEvent,
    SimpleGeneralUserEntry
};