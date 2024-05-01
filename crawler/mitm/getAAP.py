from mitmproxy import http  
  
def request(flow: http.HTTPFlow) -> None:  
    # 检查响应的URL是否是我们想要拦截的  
    if flow.request.pretty_url == "https://org.xjtu.edu.cn/workbench/taip/avoidLogin/getAAP":
        flow.request.headers["X-Platform"]="pc"