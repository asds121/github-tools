#!/usr/bin/env python3
"""DNS 探索器 - 尝试多种公共 DNS 服务器，探索更多可用的 GitHub IP"""
import sys
import socket
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib.util
from pathlib import Path

def load_module(module_path):
    """动态加载模块"""
    path = Path(module_path)
    spec = importlib.util.spec_from_file_location("tool_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

ROOT_DIR = Path(__file__).resolve().parent.parent

# 加载依赖模块
tester_module = load_module(
    "tester",
    ROOT_DIR / "GitHub-searcher-test-测速" / "github_ip_tester.py"
)
test_ips = tester_module.test_all
test_single = tester_module.test_homepage_speed

def resolve_with_dns(server, domain="github.com"):
    """使用指定 DNS 服务器解析域名"""
    try:
        # 创建 UDP 套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5)
        
        # DNS 查询数据（简化版，只支持 A 记录查询）
        query_id = 0x1234
        flags = 0x0100  # 标准查询
        questions = 1
        answer_rrs = 0
        authority_rrs = 0
        additional_rrs = 0
        
        # 构建 DNS 查询头部
        header = (
            query_id.to_bytes(2, byteorder='big') +
            flags.to_bytes(2, byteorder='big') +
            questions.to_bytes(2, byteorder='big') +
            answer_rrs.to_bytes(2, byteorder='big') +
            authority_rrs.to_bytes(2, byteorder='big') +
            additional_rrs.to_bytes(2, byteorder='big')
        )
        
        # 构建 DNS 查询问题部分
        qname = b''
        for part in domain.split('.'):
            qname += len(part).to_bytes(1, byteorder='big') + part.encode('utf-8')
        qname += b'\x00'  # 结束标记
        
        qtype = 0x0001  # A 记录
        qclass = 0x0001  # IN 类
        
        question = qname + qtype.to_bytes(2, byteorder='big') + qclass.to_bytes(2, byteorder='big')
        
        # 发送 DNS 查询
        sock.sendto(header + question, (server, 53))
        
        # 接收 DNS 响应
        response, _ = sock.recvfrom(512)
        sock.close()
        
        # 解析 DNS 响应（简化版，只提取 A 记录）
        ips = []
        offset = 12  # 跳过头部
        
        # 跳过问题部分
        while offset < len(response):
            if response[offset] == 0:
                offset += 1  # 结束标记
                break
            offset += 1 + response[offset]  # 跳过标签名
        offset += 4  # 跳过类型和类
        
        # 解析回答部分
        answer_count = int.from_bytes(response[6:8], byteorder='big')
        for _ in range(answer_count):
            # 跳过域名（压缩格式）
            if response[offset] & 0xc0 == 0xc0:
                offset += 2
            else:
                while offset < len(response):
                    if response[offset] == 0:
                        offset += 1
                        break
                    offset += 1 + response[offset]
            
            # 解析类型、类、TTL、数据长度
            rr_type = int.from_bytes(response[offset:offset+2], byteorder='big')
            offset += 2
            offset += 2  # 跳过类
            offset += 4  # 跳过 TTL
            data_len = int.from_bytes(response[offset:offset+2], byteorder='big')
            offset += 2
            
            # 提取 A 记录
            if rr_type == 0x0001:  # A 记录
                ip = '.'.join(map(str, response[offset:offset+data_len]))
                ips.append(ip)
            
            offset += data_len
        
        return list(set(ips))
    except Exception:
        return []

def run():
    """运行 DNS 探索器功能"""
    print("=" * 60)
    print("GitHub DNS 探索器")
    print("=" * 60)
    
    # 准备 DNS 服务器列表
    dns_servers = [
        "114.114.114.114",  # 国内常用 DNS
        "8.8.8.8",          # Google DNS
        "1.1.1.1",          # Cloudflare DNS
        "9.9.9.9",          # Quad9 DNS
        "208.67.222.222",   # OpenDNS
        "223.5.5.5",        # 阿里 DNS
        "223.6.6.6",        # 阿里 DNS
        "180.76.76.76"      # 百度 DNS
    ]
    
    print("\n[1/4] 准备 DNS 服务器列表...")
    print(f"  ✓ 共 {len(dns_servers)} 个 DNS 服务器")
    
    # 第二步：使用每个 DNS 服务器解析 github.com
    all_ips = set()
    dns_results = {}
    
    print("\n[2/4] 解析 DNS 获取 IP 列表...")
    
    for server in dns_servers:
        print(f"  正在使用 {server} 解析 github.com...")
        ips = resolve_with_dns(server)
        
        if ips:
            dns_results[server] = ips
            all_ips.update(ips)
            print(f"    ✓ 解析到 {len(ips)} 个 IP")
        else:
            print("    ✗ 解析失败")
    
    if not all_ips:
        print("\n✗ 所有 DNS 服务器都无法解析 github.com，退出")
        return {"success": False, "message": "无法解析 DNS"}
    
    print(f"\n✓ 共发现 {len(all_ips)} 个不同的 IP 地址")
    
    # 第三步：汇总结果，按 DNS 来源分组
    print("\n[3/4] 汇总结果，分析差异...")
    
    print("\n" + "=" * 60)
    print("DNS 服务器          解析 IP 数量    新发现 IP")
    print("-" * 60)
    
    # 计算每个 DNS 服务器的新发现 IP
    discovered_ips = set()
    for server, ips in dns_results.items():
        new_ips = [ip for ip in ips if ip not in discovered_ips]
        discovered_ips.update(ips)
        print(f"{server:<20} {len(ips):<15} {len(new_ips) if new_ips else 0} {'(' + ', '.join(new_ips) + ')' if new_ips else ''}")
    
    # 第四步：对所有发现的 IP 执行测速
    print("\n[4/4] 对所有发现的 IP 执行测速...")
    
    results = test_ips(list(all_ips))
    
    # 筛选出速度较快的 IP
    fast_ips = [r for r in results if r.get("latency") and r["latency"] < 200]
    fast_ips.sort(key=lambda x: x["latency"])
    
    print("\n" + "=" * 60)
    print("新发现 IP 测速结果")
    print("-" * 60)
    
    if fast_ips:
        print("推荐 IP（延迟 < 200ms）：")
        for r in fast_ips[:5]:
            print(f"  {r['ip']}: {r['latency']}ms {'★ 推荐' if r['latency'] < 150 else ''}")
    else:
        print("没有找到延迟低于 200ms 的 IP")
    
    # 输出 DNS 推荐配置
    print("\n" + "=" * 60)
    print("DNS 配置推荐")
    print("-" * 60)
    
    # 统计各 DNS 服务器解析的 IP 数量
    dns_stats = sorted([(server, len(ips)) for server, ips in dns_results.items()], key=lambda x: -x[1])
    
    if dns_stats:
        print("解析 IP 数量最多的 DNS 服务器：")
        for server, count in dns_stats[:3]:
            print(f"  {server}: {count} 个 IP")
        
        # 推荐解析结果最多的 DNS 服务器
        best_dns = dns_stats[0][0]
        print(f"\n推荐使用 DNS 服务器：{best_dns}")
        print(f"  解析到 {dns_stats[0][1]} 个 IP，可能包含更多优质节点")
    
    print("\n" + "=" * 60)
    print("DNS 探索完成")
    print("=" * 60)
    
    return {
        "success": True,
        "dns_results": dns_results,
        "total_ips": len(all_ips),
        "fast_ips": fast_ips,
        "best_dns": best_dns if 'best_dns' in locals() else None
    }


if __name__ == "__main__":
    run()
