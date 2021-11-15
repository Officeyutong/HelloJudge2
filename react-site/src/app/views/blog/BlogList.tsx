import { useEffect, useState } from "react";
import { useParams } from "react-router";
import { Link } from "react-router-dom";
import { Button, Card, Container, Dimmer, Grid, Header, Label, Loader, Pagination, Segment, Image, Divider } from "semantic-ui-react";
import { PUBLIC_URL } from "../../App";
import { toLocalTime, useDocumentTitle, useProfileImageMaker } from "../../common/Utils";
import UserLink from "../utils/UserLink";
import blogClient from "./client/BlogClient";
import { BlogListEntry, BlogUserData } from "./client/types";

const BlogList: React.FC<{}> = () => {
    const { uid } = useParams<{ uid: string }>();
    const numberUID = parseInt(uid);
    const [loading, setLoading] = useState(false);
    const [userData, setUserData] = useState<null | BlogUserData>(null);
    const [data, setData] = useState<BlogListEntry[]>([]);
    const [pageCount, setPageCount] = useState(0);
    const [page, setPage] = useState(0);
    const [managable, setManagable] = useState(false);
    const [loaded, setLoaded] = useState(false);
    const loadPage = async (page: number) => {
        setLoading(true);
        try {
            const resp = await blogClient.getBlogList(numberUID, page);
            setUserData(resp.userData);
            setPageCount(resp.pageCount);
            setData(resp.data);
            setManagable(resp.managable);
            setLoading(false);
            setLoaded(true);
            setPage(page);
        } catch { } finally {

        }
    };
    useEffect(() => {
        if (!loaded) loadPage(1);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [loaded]);
    useDocumentTitle(`${userData?.username || "加载中..."} - 博客列表`);
    const makeImg = useProfileImageMaker();

    return <>
        {!loaded && loading && <>
            <Segment stacked>
                <div style={{ height: "400px" }}></div>
                <Dimmer active>
                    <Loader></Loader>
                </Dimmer>
            </Segment>
        </>}
        {loaded && userData !== null && <>
            <Header as="h1">
                {userData.username} 的博客
            </Header>
            <Grid columns="2">
                <Grid.Column width="12">
                    <Segment stacked>
                        {loading && <Dimmer active>
                            <Loader></Loader>
                        </Dimmer>}
                        {data.length === 0 && <Container textAlign="center">
                            这个人很懒...还没写过博客..
                        </Container>}

                        {data.length !== 0 && <>
                            {data.map((item, i) => <Card key={i} fluid style={{ marginBottom: "20px" }}>
                                <Card.Content>
                                    <Card.Header>
                                        <Link to={`${PUBLIC_URL}/show_discussion/${item.id}`}>{item.title}</Link>
                                        {item.private && <Label color="red">私有</Label>}
                                    </Card.Header>
                                    <Card.Meta>
                                        <div style={{ fontSize: "small" }}>
                                            <div>发表于 {toLocalTime(item.time)}</div>
                                            共有 {item.commentCount} 条评论
                                            {item.lastCommentAt && <div>
                                                最后评论于 {toLocalTime(item.lastCommentAt)}
                                            </div>}
                                        </div>
                                    </Card.Meta>
                                    <Card.Description>
                                        {item.summary}
                                    </Card.Description>
                                </Card.Content>
                                <Card.Content extra>
                                    {managable && <Button size="tiny" as={Link} to={`${PUBLIC_URL}/blog/edit/${item.id}`}>
                                        编辑
                                    </Button>}
                                </Card.Content>
                            </Card>)}
                        </>}
                        <Divider></Divider>
                        <Container textAlign="center">
                            <Pagination
                                totalPages={pageCount}
                                activePage={page}
                                onPageChange={(_, d) => loadPage(d.activePage as number)}
                            ></Pagination>
                        </Container>
                    </Segment>

                </Grid.Column>
                <Grid.Column width="4">
                    <div style={{ position: "fixed" }}>
                        <Card>
                            <Image src={makeImg(userData.email)}></Image>
                            <Card.Content>
                                <Card.Header>
                                    <UserLink data={userData}></UserLink>
                                </Card.Header>
                                <Card.Meta>
                                    <span>{userData.email}</span>
                                </Card.Meta>
                            </Card.Content>
                            <Card.Content extra>
                                共有 {userData.publicBlogCount} 篇公开博客
                            </Card.Content>
                            {managable && <Card.Content extra>
                                <Button size="tiny" color="green" as={Link} to={`${PUBLIC_URL}/blog/edit/`}> 新建博客</Button>
                            </Card.Content>}
                        </Card>
                    </div>
                </Grid.Column>
            </Grid>
        </>}
    </>;
};

export default BlogList;