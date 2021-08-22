import React from "react";
import { List } from "semantic-ui-react";
import { UserProfileResponse } from "../client/types";

const JoinedTeamsTab: React.FC<{ data: UserProfileResponse["joined_teams"] }> = ({ data }) => {
    return <div>
        <List>
            {data.map((x, i) => <List.Item key={i
            }>
                <a href={`/team/${x.id}`}>#{x.id}. {x.name}</a>
            </List.Item>)}
        </List>
    </div>;
}

export default JoinedTeamsTab;
