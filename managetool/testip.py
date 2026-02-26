import socket
import requests
import time
from requests.exceptions import RequestException, ConnectionError, Timeout

def check_baidu():
    """检查能否访问百度（国内常用网站）"""
    try:
        start_time = time.time()
        response = requests.get('https://www.baidu.com', timeout=5)
        # 状态码200且响应时间小于3秒视为有效访问
        return response.status_code == 200 and (time.time() - start_time) < 3
    except RequestException:
        return False

def check_google():
    """检查能否访问谷歌（国外常用网站）"""
    try:
        start_time = time.time()
        response = requests.get('https://www.google.com', timeout=5)
        return response.status_code == 200 and (time.time() - start_time) < 3
    except RequestException:
        return False

def check_dns_resolution():
    """检查国内外域名解析情况"""
    try:
        # 尝试解析国内域名
        socket.gethostbyname('www.baidu.com')
        # 尝试解析国外域名
        socket.gethostbyname('www.google.com')
        return True
    except socket.gaierror:
        return False

def check_public_ip():
    """通过IP查询服务判断地理位置"""
    try:
        # 使用多个IP查询服务以提高准确性
        ip_services = [
            'https://api.ipify.org?format=json',
            'https://ipapi.co/json/',
            'https://ip.cn/ipjson'
        ]
        
        for service in ip_services:
            try:
                response = requests.get(service, timeout=5)
                data = response.json()
                
                # 不同服务返回格式不同，需要分别处理
                if 'country' in data:
                    return data['country'].lower() == 'china'
                elif 'country_name' in data:
                    return data['country_name'].lower() == 'china'
                elif 'country_code' in data:
                    return data['country_code'].lower() == 'cn'
            except:
                continue
                
        return False
    except Exception:
        return False

def check_wechat_platform():
    """检查能否访问微信公众平台（国内常用服务）"""
    try:
        response = requests.get('https://mp.weixin.qq.com', timeout=5)
        # 302是正常重定向，也视为可访问
        return response.status_code in [200, 302]
    except RequestException:
        return False

def check_youtube():
    """检查能否访问YouTube（国外常用服务）"""
    try:
        response = requests.get('https://www.youtube.com', timeout=5)
        return response.status_code == 200
    except RequestException:
        return False

def check_china_cdn():
    """检查能否访问国内CDN节点"""
    try:
        response = requests.get('https://cdn.baidustatic.com', timeout=3)
        return response.status_code == 200
    except RequestException:
        return False

def comprehensive_check():
    """综合多种检测结果判断网络环境"""
    score = 0
    
    # 国内服务可访问加分
    if check_baidu():
        score += 2
    if check_wechat_platform():
        score += 2
    if check_china_cdn():
        score += 1
    
    # 国外服务不可访问加分（国内通常无法直接访问）
    if not check_google():
        score += 1
    if not check_youtube():
        score += 1
    
    # DNS解析正常加分
    if check_dns_resolution():
        score += 1
    
    # IP查询显示中国加分
    if check_public_ip():
        score += 3
    
    # 总分10分，超过5分判断为国内
    return score > 5

def main():
    print("正在进行网络环境检测，请稍候...\n")
    
    # 显示各项检测结果
    print(f"百度访问测试: {'成功' if check_baidu() else '失败'}")
    print(f"谷歌访问测试: {'成功' if check_google() else '失败'}")
    print(f"微信平台访问测试: {'成功' if check_wechat_platform() else '失败'}")
    print(f"YouTube访问测试: {'成功' if check_youtube() else '失败'}")
    print(f"国内CDN访问测试: {'成功' if check_china_cdn() else '失败'}")
    print(f"DNS解析测试: {'正常' if check_dns_resolution() else '异常'}")
    print(f"IP地理位置测试: {'中国' if check_public_ip() else '国外'}\n")
    
    # 综合判断并输出结果
    if comprehensive_check():
        print("综合判断: 当前网络环境很可能在国内")
    else:
        print("综合判断: 当前网络环境很可能在国外")

if __name__ == "__main__":
    main()
    