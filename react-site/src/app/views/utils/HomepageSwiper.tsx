import React from "react";
import { HomepageSwiperList } from "../admin/client/types";
import SwiperCore, { Pagination } from "swiper";
import { Swiper, SwiperSlide } from "swiper/react";
import { Image } from "semantic-ui-react";
import 'swiper/swiper.scss';
import 'swiper/components/pagination/pagination.scss';
SwiperCore.use([Pagination])
const HomepageSwiper: React.FC<{ data: HomepageSwiperList }> = ({ data }) => {
    return <Swiper
        slidesPerView={1}
        pagination={{ clickable: true }}
        autoplay={{
            delay: 5000
        }}>
        {data.map((x, i) => <SwiperSlide key={i}>
            <a href={x.link_url} target="_blank" rel="noreferrer">
                <Image src={x.image_url}></Image>
            </a>
        </SwiperSlide>)}
    </Swiper>
};

export default HomepageSwiper;
