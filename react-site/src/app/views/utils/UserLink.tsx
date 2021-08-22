import React from "react";
import { GeneralUserEntry } from "../../common/types";

type UserLinkProps = {
    data: Pick<GeneralUserEntry, "uid" | "username">;
};

const UserLink: React.FC<UserLinkProps> = ({
    data
}) => {
    return <a target="_blank" rel="noreferrer" href={`/profile/${data.uid}`}>{data.username}</a>;
};

export default UserLink;