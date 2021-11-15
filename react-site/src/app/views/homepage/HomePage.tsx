import React, { useEffect, useRef, useState } from "react";
import { useSelector } from "react-redux";
import { Dimmer, Divider, Header, Loader, Rail, Ref, Segment, Sticky } from "semantic-ui-react";
import { useDocumentTitle } from "../../common/Utils";
import { StateType } from "../../states/Manager";
import { adminClient } from "../admin/client/AdminClient";
import { HomepageSwiperList } from "../admin/client/types";
import feedClient from "../feed/client/FeedClient";
import { FeedStreamEntry } from "../feed/client/types";
import FeedArea from "../feed/FeedArea";
import HomepageSwiper from "../utils/HomepageSwiper";
import homepageClient from "./client/HomePageClient";
import { HomePageData } from "./client/types";
import { BroadcastBox, FriendLinkBox, ProblemQuickAccessBox, ProblemSearchBox, ProblemtodoBox, ToolBox } from "./HomePageBoxes";
import HomepageRanklistArea from "./HomePageRanklistArea";

const HomePage: React.FC<{}> = () => {
    useDocumentTitle("主页");
    const appName = useSelector((s: StateType) => s.userState.userData.appName);
    const contextRef = useRef(null);
    const [loaded, setLoaded] = useState(false);
    const [loading, setLoading] = useState(false);
    const [homePageData, setHomePageData] = useState<HomePageData | null>(null);
    const [swipers, setSwipers] = useState<HomepageSwiperList>([]);
    const [feed, setFeed] = useState<FeedStreamEntry[]>([]);
    // const [feedLoaded, setFeedLoaded] = useState(false);
    const alreadyLogin = useSelector((s: StateType) => s.userState.login);
    useEffect(() => {
        if (!loaded) {
            (async () => {
                try {
                    setLoading(true);
                    const [d1, d2, d3] = await Promise.all([homepageClient.loadData(), adminClient.getHomepageSwiperList(), feedClient.getFeedStream()]);
                    // setFeedLoaded(alreadyLogin);
                    setHomePageData(d1);
                    setSwipers(d2);
                    setFeed(d3);
                    setLoaded(true);
                } catch (e) { } finally { setLoading(false); }
            })();
        }
    }, [loaded, alreadyLogin])

    return <div>
        <Header as="h1">{appName}</Header>
        <Divider></Divider>
        <div>
            <Ref innerRef={contextRef}>
                <Segment stacked style={{ maxWidth: "75%" }}>
                    <div >
                        {loading && <Dimmer active={loading}>
                            <Loader></Loader>
                        </Dimmer>}
                        <HomepageSwiper data={swipers}></HomepageSwiper>
                        <Divider></Divider>
                        <FeedArea data={feed}></FeedArea>
                        {homePageData !== null && homePageData.showRanklist && <>
                            <Divider></Divider>
                            <HomepageRanklistArea></HomepageRanklistArea>
                        </>}
                    </div>
                    <Rail position="right" >
                        <Sticky context={contextRef}>
                            {loaded && <>
                                <ProblemQuickAccessBox></ProblemQuickAccessBox>
                                <ProblemSearchBox></ProblemSearchBox>
                                <ToolBox data={homePageData!.toolbox}></ToolBox>
                                <BroadcastBox></BroadcastBox>
                                <ProblemtodoBox></ProblemtodoBox>
                                <FriendLinkBox data={homePageData!.friendLinks}></FriendLinkBox>
                            </>}
                        </Sticky>
                    </Rail>
                </Segment>
            </Ref>
        </div>
    </div>;
};


export default HomePage;
