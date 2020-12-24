# code=utf-8
from bs4 import BeautifulSoup
import requests as rq


curl_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36',
    # 'Origin': 'http://www.zuidazy4.com', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,
    # image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Referer':
    # 'http://www.zuidazy4.com/index.php?m=vod-search', 'Accept-Language': 'zh-CN,zh;q=0.9', 'Cache-Control':
    # 'max-age=0',

}

url_host = "http://www.zuidazy4.com"


def search_video(video_name):
    url_search = "http://www.zuidazy4.com/index.php?m=vod-search"
    data_para = {
        "wd": video_name,
        "submit": "search",
    }

    resp = rq.post(url=url_search, headers=curl_header, data=data_para)
    soup = BeautifulSoup(resp.content, "lxml")
    card_video = soup.find(name='div', attrs={"class": "xing_vb"})
    list_video = card_video.find_all("ul")[1:-1]
    list_video_info = [parse_video_info(one_video) for one_video in list_video]
    return list_video_info


def parse_video_info(one_video):
    span_name = one_video.find(name="span", attrs={"class": "xing_vb4"})
    href = span_name.find("a").get("href")
    type_name = one_video.find(name="span", attrs={"class": "xing_vb5"})
    update_time = one_video.find(name="span", attrs={"class": "xing_vb6"})
    video_info = {
        "video_name": span_name.text,
        "video_uri": href,
        "video_type": type_name.text,
        "update_time": update_time.text,
    }

    return video_info


def get_video_info(video_uri):
    url = "{}{}".format(url_host, video_uri)
    resp = rq.get(url, headers=curl_header)
    soup = BeautifulSoup(resp.content, "lxml")
    video_header = soup.find(name="div", attrs={"class": "vodh"})
    video_title = video_header.find("h2").text
    video_intros = soup.find(name="div", attrs={"class": "vodinfobox"})
    video_intro_info = parse_video_intro(video_intros)
    video_intro_info["video_name"] = video_title
    m3u8_list = soup.find(name="div", attrs={"id": "play_1"}).find_all("li")
    res_m3u8_list = [m3_info.text.split("$") for m3_info in m3u8_list]

    return video_intro_info, res_m3u8_list


def parse_video_intro(video_intros):
    more_info = video_intros.find(name="span", attrs={"class": "more"}).get("txt")
    list_info = video_intros.find_all("li")
    list_info_text = [li.text for li in list_info]
    director = get_info_value("导演", list_info_text)
    actor = get_info_value("主演", list_info_text)
    time_dur = get_info_value("片长", list_info_text)
    up_time = get_info_value("上映", list_info_text)
    intro_info = {
        "director": director,
        "actor": actor,
        "up_time": up_time,
        "time_dur": time_dur,
        "more_info": more_info
    }

    return intro_info


def get_info_value(val_name, list_info_text):
    for txt in list_info_text:
        if val_name in txt:
            return txt.split("：")[-1].strip()
    return "未知"


if __name__ == '__main__':

    video_infos = search_video("演员请就位")
    for video_info in video_infos:
        print(video_info)

    intro, m3_list = get_video_info(video_infos[0]["video_uri"])
    print(intro)

    for m in m3_list:
        print(m)
