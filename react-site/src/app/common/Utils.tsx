import React, { useEffect, useState, useCallback } from "react";
import { InputOnChangeData } from "semantic-ui-react";
import md5 from "md5";
import { useSelector } from "react-redux";
import { StateType } from "../states/Manager";
import { sprintf } from "sprintf-js";
import createPersistedState from "use-persisted-state";
import { DateTime } from "luxon";

export const usePreferredMemoryUnit = createPersistedState("hj2-preferred-memory-unit");


const useDocumentTitle: (title: string) => void = (title: string) => {
    const appName = useSelector((s: StateType) => s.userState.userData.appName);
    useEffect(() => {
        document.title = `${title} - ${appName}`;
        return () => { document.title = appName };
    }, [title, appName]);
};
type onChangeType = ((event: React.ChangeEvent<HTMLInputElement>, data: InputOnChangeData) => void);

const useInputValue: (text?: string) => { value: string; onChange: onChangeType } = (text: string = "") => {
    const [value, setValue] = useState(text);
    let onChange: onChangeType = useCallback((_, d) => {
        setValue(d.value);
    }, []);
    return { value, onChange };
};

// const makeGravatarImageURL: (email: string) => string = (email) => {
//     const hashval = md5(email.trim().toLowerCase());
//     return `https://gravatar.loli.net/avatar/${hashval}`;
// };

function useProfileImageMaker(): (email: string, size?: number | string) => string {
    const profileURL = useSelector((s: StateType) => s.userState.userData.gravatarURL);
    return (email, size) => {
        return `${profileURL}${md5(email)}` + (size ? `?size=${size}` : "");
    };
}
export function usePasswordSalt() {
    const salt = useSelector((s: StateType) => s.userState.userData.salt);
    return salt;
}
/**
 * -1表示未登录
 * 
*/
export function useCurrentUid() {
    const uid = useSelector((s: StateType) => s.userState.userData.uid);
    return uid;
}
export function useAlreadyLogin() {
    const login = useSelector((s: StateType) => s.userState.login);
    return login;
}
export function secondsToString(totSecond: number): string {
    const seconds = totSecond % 60;
    const minutes = (Math.floor(totSecond / 60)) % 60;
    const hours = Math.floor(totSecond / 3600);
    return sprintf("%2d小时 %2d分钟 %2d秒", hours, minutes, seconds);
};
export function toLocalTime(seconds: number): string {
    return DateTime.fromSeconds(seconds).toJSDate().toLocaleString();
}
export {
    useDocumentTitle,
    useInputValue,
    useProfileImageMaker
};

export type {
    onChangeType
};