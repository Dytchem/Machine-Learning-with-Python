from mitmproxy import http  
  
def response(flow: http.HTTPFlow) -> None:  
    # 检查响应的URL是否是我们想要拦截的  
    if flow.request.pretty_url == "http://jwapp.xjtu.edu.cn/api/biz/v410/common/local":  
        # 修改响应体  
        json_data = """{  
   "code": 200,  
   "msg": "操作成功",  
   "data": [  
       "en_US",  
       "zh_CN",  
       "es_ES",  
       "fr_FR",  
       "de_DE",  
       "ja_JP",  
       "ko_KR",  
       "pt_BR",  
       "ru_RU",  
       "it_IT",  
       "ar_SA",  
       "nl_NL",  
       "pl_PL",  
       "cs_CZ",  
       "sv_SE",  
       "da_DK",  
       "no_NO",  
       "hu_HU",  
       "fi_FI",  
       "tr_TR",  
       "ro_RO",  
       "bg_BG",  
       "el_GR",  
       "he_IL",  
       "hi_IN",  
       "id_ID",  
       "ms_MY",  
       "th_TH",  
       "vi_VN",  
       "uk_UA",  
       "ca_ES",  
       "eu_ES"  
   ]  
}"""  
        # 将字符串编码为字节串  
        flow.response.content = json_data.encode('utf-8')  
        # 你也可以修改响应头等其他属性  
        # flow.response.headers["Some-Header"] = "new value"