# services/network.py
import asyncio
import time
import socket
import ssl
import ipaddress
import platform
from datetime import datetime, timezone
import aiohttp
import dns.resolver
import psutil

# Portas padrão mais utilizadas em auditorias de rede
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP (Área de Trabalho Remota)",
    5432: "PostgreSQL",
    8080: "HTTP Proxy/Alt",
    8443: "HTTPS Alt",
    25565: "Minecraft Server",
}


async def ping_host(host: str, timeout_ms: int = 1500) -> tuple[bool, float, str]:
    """Executa um ping assíncrono multiplataforma."""
    clean_host = host.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0].strip()
    is_windows = platform.system().lower() == "windows"

    cmd = ["ping", "-n", "1", "-w", str(timeout_ms), clean_host] if is_windows else ["ping", "-c", "1", "-W", str(max(1, timeout_ms // 1000)), clean_host]

    start = time.perf_counter()
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=3.0)
        elapsed_ms = (time.perf_counter() - start) * 1000

        output = stdout.decode("latin-1", errors="ignore")
        if proc.returncode == 0 and ("TTL=" in output or "ttl=" in output):
            return True, elapsed_ms, f"{elapsed_ms:.1f} ms"
        else:
            return False, 0.0, "Esgotado o tempo limite (Timeout)"
    except Exception as e:
        return False, 0.0, str(e)


async def check_http(url: str, timeout_s: float = 4.0) -> tuple[bool, int, float, str]:
    """Verifica a saúde de um site ou API HTTP/HTTPS."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    start = time.perf_counter()
    try:
        timeout = aiohttp.ClientTimeout(total=timeout_s)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, allow_redirects=True) as resp:
                elapsed_ms = (time.perf_counter() - start) * 1000
                is_up = 200 <= resp.status < 400
                return is_up, resp.status, elapsed_ms, f"Status {resp.status} ({elapsed_ms:.1f} ms)"
    except Exception as e:
        return False, 0, 0.0, f"Falha na conexão: {type(e).__name__}"


async def check_tcp_port(host: str, port: int, timeout_s: float = 2.0) -> tuple[bool, float]:
    """Verifica se uma porta TCP específica está respondendo."""
    clean_host = host.replace("http://", "").replace("https://", "").split("/")[0].strip()
    start = time.perf_counter()
    try:
        conn = asyncio.open_connection(clean_host, port)
        _, writer = await asyncio.wait_for(conn, timeout=timeout_s)
        elapsed_ms = (time.perf_counter() - start) * 1000
        writer.close()
        await writer.wait_closed()
        return True, elapsed_ms
    except Exception:
        return False, 0.0


async def port_scan(host: str, custom_ports: list[int] = None) -> list[dict]:
    """Varre portas concorrentemente com asyncio para alta performance."""
    ports_to_scan = custom_ports or list(COMMON_PORTS.keys())
    clean_host = host.replace("http://", "").replace("https://", "").split("/")[0].strip()

    async def scan_single(port: int):
        is_open, lat = await check_tcp_port(clean_host, port, timeout_s=1.0)
        return {
            "port": port,
            "service": COMMON_PORTS.get(port, "Desconhecido"),
            "open": is_open,
            "latency": lat
        }

    tasks = [scan_single(p) for p in ports_to_scan]
    results = await asyncio.gather(*tasks)
    return sorted(results, key=lambda x: x["port"])


def calculate_subnet(cidr: str) -> dict:
    """Calcula todas as informações de sub-rede para IPv4 ou IPv6."""
    net = ipaddress.ip_network(cidr.strip(), strict=False)

    if net.version == 4:
        # IPv4
        netmask = str(net.netmask)
        wildcard = str(ipaddress.IPv4Address(int(net.hostmask)))
        broadcast = str(net.broadcast_address)
        network_addr = str(net.network_address)
        total_hosts = net.num_addresses
        usable_hosts = max(total_hosts - 2, 1) if net.prefixlen < 31 else total_hosts

        hosts_iter = net.hosts()
        try:
            first_host = str(next(hosts_iter))
            last_host = str(list(net.hosts())[-1]) if usable_hosts > 1 else first_host
        except StopIteration:
            first_host = network_addr
            last_host = broadcast

        # Classe do IP
        first_octet = int(network_addr.split(".")[0])
        if first_octet < 128:
            ip_class = "Classe A"
        elif first_octet < 192:
            ip_class = "Classe B"
        elif first_octet < 224:
            ip_class = "Classe C"
        elif first_octet < 240:
            ip_class = "Classe D (Multicast)"
        else:
            ip_class = "Classe E (Experimental)"

        tipo = "Privado (RFC 1918)" if net.is_private else ("Loopback" if net.is_loopback else "Público")

        return {
            "version": "IPv4",
            "cidr": str(net),
            "prefix": net.prefixlen,
            "netmask": netmask,
            "wildcard": wildcard,
            "network": network_addr,
            "broadcast": broadcast,
            "first_host": first_host,
            "last_host": last_host,
            "usable_hosts": usable_hosts,
            "total_addresses": total_hosts,
            "class": ip_class,
            "type": tipo
        }
    else:
        # IPv6
        return {
            "version": "IPv6",
            "cidr": str(net),
            "prefix": net.prefixlen,
            "network": str(net.network_address),
            "netmask": str(net.netmask),
            "total_addresses": net.num_addresses,
            "type": "Privado / ULA" if net.is_private else "Global Unicast / Público"
        }


def query_dns(domain: str, record_type: str = "A") -> list[str]:
    """Consulta registros DNS de um domínio."""
    clean_domain = domain.replace("http://", "").replace("https://", "").split("/")[0].strip()
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3.0
    resolver.lifetime = 3.0

    try:
        answers = resolver.resolve(clean_domain, record_type.upper())
        return [str(rdata) for rdata in answers]
    except dns.resolver.NoAnswer:
        return ["Nenhum registro encontrado para este tipo."]
    except dns.resolver.NXDOMAIN:
        return ["Domínio não existe (NXDOMAIN)."]
    except Exception as e:
        return [f"Erro: {e}"]


def check_ssl(domain: str) -> dict:
    """Verifica validade e detalhes do certificado SSL/TLS."""
    clean_domain = domain.replace("http://", "").replace("https://", "").split("/")[0].strip()
    context = ssl.create_default_context()
    conn = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=clean_domain)
    conn.settimeout(3.0)

    try:
        conn.connect((clean_domain, 443))
        cert = conn.getpeercert()
        conn.close()

        # Validade
        expire_date_str = cert["notAfter"]
        # Formato ex: 'May 15 12:00:00 2026 GMT'
        expire_time = time.strptime(expire_date_str, "%b %d %H:%M:%S %Y %Z")
        expire_timestamp = time.mktime(expire_time)
        now_timestamp = time.time()
        days_left = int((expire_timestamp - now_timestamp) / 86400)

        # Emissor
        issuer_dict = dict(x[0] for x in cert.get("issuer", []))
        issuer = issuer_dict.get("commonName") or issuer_dict.get("organizationName") or "Desconhecido"

        return {
            "valid": days_left > 0,
            "days_left": days_left,
            "expires_at": time.strftime("%d/%m/%Y %H:%M", expire_time),
            "issuer": issuer,
            "subject": dict(x[0] for x in cert.get("subject", [])).get("commonName", clean_domain)
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}


def get_system_telemetry() -> dict:
    """Coleta métricas de hardware e tráfego de rede da máquina local."""
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_cores = psutil.cpu_count(logical=True)

    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    net_io = psutil.net_io_counters()

    # Formatação de bytes
    def format_bytes(bytes_num):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_num < 1024.0:
                return f"{bytes_num:.1f} {unit}"
            bytes_num /= 1024.0
        return f"{bytes_num:.1f} PB"

    boot_time = datetime.fromtimestamp(psutil.boot_time(), timezone.utc).strftime("%d/%m/%Y às %H:%M")

    return {
        "cpu_percent": cpu_percent,
        "cpu_cores": cpu_cores,
        "ram_percent": ram.percent,
        "ram_used": format_bytes(ram.used),
        "ram_total": format_bytes(ram.total),
        "disk_percent": disk.percent,
        "disk_free": format_bytes(disk.free),
        "disk_total": format_bytes(disk.total),
        "bytes_sent": format_bytes(net_io.bytes_sent),
        "bytes_recv": format_bytes(net_io.bytes_recv),
        "packets_sent": net_io.packets_sent,
        "packets_recv": net_io.packets_recv,
        "boot_time": boot_time
    }


# ==========================================
# 🔍 DIAGNÓSTICOS AVANÇADOS DE REDE
# ==========================================

async def run_traceroute(target: str, max_hops: int = 18) -> list[dict]:
    """Executa um traceroute multiplataforma e retorna a lista de saltos (hops)."""
    clean_target = target.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0].strip()
    is_windows = platform.system().lower() == "windows"

    cmd = ["tracert", "-d", "-h", str(max_hops), "-w", "1000", clean_target] if is_windows else ["traceroute", "-n", "-m", str(max_hops), "-w", "1", clean_target]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30.0)
        output = stdout.decode("latin-1", errors="ignore")

        hops = []
        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            # Windows tracert hop line starts with number: '1    <1 ms    <1 ms    <1 ms  192.168.1.1'
            if parts and parts[0].isdigit():
                hop_num = int(parts[0])
                if "*" in parts and len(parts) <= 4:
                    hops.append({"hop": hop_num, "ip": "* * * (Tempo limite)", "rtt": "Timeout"})
                else:
                    ip = parts[-1]
                    # pega rtt se disponível
                    rtts = [p for p in parts if "ms" in p or p.isdigit()]
                    rtt_str = rtts[0] + " ms" if rtts else "OK"
                    hops.append({"hop": hop_num, "ip": ip, "rtt": rtt_str})
        return hops
    except Exception as e:
        return [{"hop": 1, "ip": f"Erro no traceroute: {e}", "rtt": "Error"}]


async def lookup_whois_and_geo(query: str) -> dict:
    """Consulta informações de ASN, Geolocalização e Provedor (ISP) via RDAP/IP-API."""
    clean_query = query.replace("http://", "").replace("https://", "").split("/")[0].split(":")[0].strip()
    url = f"http://ip-api.com/json/{clean_query}?fields=status,message,country,countryCode,regionName,city,zip,lat,lon,timezone,isp,org,as,query"

    try:
        timeout = aiohttp.ClientTimeout(total=5.0)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                data = await resp.json()
                if data.get("status") == "success":
                    return {
                        "success": True,
                        "ip": data.get("query"),
                        "country": f"{data.get('country')} ({data.get('countryCode')})",
                        "city": f"{data.get('city')}, {data.get('regionName')}",
                        "isp": data.get("isp"),
                        "org": data.get("org") or data.get("isp"),
                        "asn": data.get("as", "N/A"),
                        "timezone": data.get("timezone"),
                        "coords": f"{data.get('lat')}, {data.get('lon')}"
                    }
                else:
                    return {"success": False, "error": data.get("message", "IP ou domínio não encontrado.")}
    except Exception as e:
        return {"success": False, "error": str(e)}


TOP_MAC_VENDORS = {
    "00000C": "Cisco Systems",
    "000142": "Cisco Systems",
    "000143": "Cisco Systems",
    "000163": "Cisco Systems",
    "000164": "Cisco Systems",
    "0001C7": "Cisco Systems",
    "0001C9": "Cisco Systems",
    "0008E3": "Cisco Systems",
    "000C29": "VMware, Inc.",
    "005056": "VMware, Inc.",
    "00155D": "Microsoft Corporation (Hyper-V)",
    "001A2B": "Ayecom Technology Co., Ltd.",
    "001B67": "Intel Corporate",
    "001CC0": "Intel Corporate",
    "4851B7": "Intel Corporate",
    "001E8C": "MikroTik",
    "488F5A": "MikroTik",
    "64D154": "MikroTik",
    "B869F4": "MikroTik",
    "CC2DE0": "MikroTik",
    "D4CA6D": "MikroTik",
    "E48D8C": "MikroTik",
    "001882": "Huawei Technologies",
    "001E10": "Huawei Technologies",
    "00259E": "Huawei Technologies",
    "0425C5": "Huawei Technologies",
    "08E84F": "Huawei Technologies",
    "001F6B": "TP-Link Corporation",
    "14CF92": "TP-Link Corporation",
    "50C7BF": "TP-Link Corporation",
    "984827": "TP-Link Corporation",
    "C006C3": "TP-Link Corporation",
    "000456": "Cambium Networks",
    "00156D": "Ubiquiti Networks",
    "24A43C": "Ubiquiti Networks",
    "68D79A": "Ubiquiti Networks",
    "788A20": "Ubiquiti Networks",
    "B4FBE4": "Ubiquiti Networks",
    "FCECDA": "Ubiquiti Networks",
    "B827EB": "Raspberry Pi Foundation",
    "DCA632": "Raspberry Pi Trading",
    "E45F01": "Raspberry Pi Trading",
    "000C42": "MikroTik",
    "001A8C": "Sophos Ltd",
    "00090F": "Fortinet, Inc.",
    "704CA5": "Fortinet, Inc.",
    "0001E8": "Force10 Networks",
    "000B86": "Aruba Networks",
    "001A1E": "Aruba Networks",
    "00246C": "Aruba Networks",
    "0010E0": "Juniper Networks",
    "001F12": "Juniper Networks",
    "002688": "Juniper Networks",
    "3C6104": "Apple, Inc.",
    "A483E7": "Apple, Inc.",
    "F01898": "Apple, Inc.",
    "001A11": "Google, Inc.",
    "F4F5E8": "Google, Inc.",
    "3C5AB4": "Google, Inc.",
    "0014D1": "Trendnet",
    "001150": "Belkin International",
}


async def lookup_mac_oui(mac_str: str) -> dict:
    """Identifica o fabricante de uma placa de rede a partir do endereço MAC."""
    clean_mac = mac_str.replace(":", "").replace("-", "").replace(".", "").strip().upper()
    if len(clean_mac) < 6:
        return {"success": False, "error": "Endereço MAC inválido. Forneça ao menos 6 caracteres hexadecimais (ex: 00:1A:2B:3C:4D:5E)."}

    oui = clean_mac[:6]
    formatted_oui = f"{oui[0:2]}:{oui[2:4]}:{oui[4:6]}"

    # Checa dicionário local
    if oui in TOP_MAC_VENDORS:
        return {
            "success": True,
            "mac": mac_str,
            "oui": formatted_oui,
            "vendor": TOP_MAC_VENDORS[oui],
            "source": "Base OUI Local"
        }

    # Fallback online gratuito
    try:
        timeout = aiohttp.ClientTimeout(total=4.0)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(f"https://api.maclookup.app/v2/macs/{clean_mac}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    company = data.get("company")
                    if company:
                        return {
                            "success": True,
                            "mac": mac_str,
                            "oui": formatted_oui,
                            "vendor": company,
                            "source": "IEEE Global Database"
                        }
    except Exception:
        pass

    return {
        "success": False,
        "mac": mac_str,
        "oui": formatted_oui,
        "error": "Fabricante desconhecido ou não registrado para este prefixo OUI."
    }


# ==========================================
# 🧮 MODO ACADÊMICO & CISCO CCNA (VLSM / TEMPLATES)
# ==========================================

def calculate_vlsm(base_cidr: str, requirements: list[tuple[str, int]]) -> dict:
    """Calcula a alocação de sub-redes VLSM (Variable Length Subnet Mask)."""
    import math
    base_net = ipaddress.ip_network(base_cidr.strip(), strict=False)
    if base_net.version != 4:
        raise ValueError("O cálculo de VLSM é aplicável exclusivamente a redes IPv4.")

    # Ordena requisitos em ordem decrescente de número de hosts
    sorted_reqs = sorted(requirements, key=lambda x: x[1], reverse=True)

    allocated_subnets = []
    current_ip_int = int(base_net.network_address)
    total_space_used = 0

    for name, req_hosts in sorted_reqs:
        # hosts utilizáveis = 2^bits - 2. Então precisamos de bits tais que 2^bits >= req_hosts + 2
        needed_capacity = req_hosts + 2
        host_bits = math.ceil(math.log2(needed_capacity))
        prefix = 32 - host_bits
        allocated_capacity = 2 ** host_bits
        usable = allocated_capacity - 2

        # Alinha endereço com a máscara de sub-rede
        if current_ip_int % allocated_capacity != 0:
            current_ip_int = ((current_ip_int // allocated_capacity) + 1) * allocated_capacity

        sub_net = ipaddress.IPv4Network((current_ip_int, prefix), strict=False)

        # Checa se coube no bloco base
        if sub_net.broadcast_address > base_net.broadcast_address:
            raise ValueError(f"Espaço insuficiente no bloco {base_cidr}! A sub-rede '{name}' ({req_hosts} hosts) excedeu o limite.")

        hosts_list = list(sub_net.hosts())
        first_h = str(hosts_list[0]) if hosts_list else str(sub_net.network_address)
        last_h = str(hosts_list[-1]) if hosts_list else str(sub_net.broadcast_address)

        allocated_subnets.append({
            "name": name,
            "needed_hosts": req_hosts,
            "usable_hosts": usable,
            "allocated_hosts": allocated_capacity,
            "cidr": str(sub_net),
            "netmask": str(sub_net.netmask),
            "wildcard": str(ipaddress.IPv4Address(int(sub_net.hostmask))),
            "network": str(sub_net.network_address),
            "first_host": first_h,
            "last_host": last_h,
            "broadcast": str(sub_net.broadcast_address)
        })

        current_ip_int += allocated_capacity
        total_space_used += allocated_capacity

    return {
        "base_network": str(base_net),
        "total_addresses": base_net.num_addresses,
        "used_addresses": total_space_used,
        "free_addresses": base_net.num_addresses - total_space_used,
        "subnets": allocated_subnets
    }


def generate_cisco_config(template_type: str, params: dict = None) -> str:
    """Gera scripts de configuração prontos para switches e roteadores Cisco."""
    params = params or {}
    t = template_type.lower()

    if t in ["vlan", "vlans"]:
        vlan_id = params.get("vlan_id", "10")
        vlan_name = params.get("vlan_name", "FINANCEIRO")
        access_port = params.get("access_port", "GigabitEthernet0/1")
        trunk_port = params.get("trunk_port", "GigabitEthernet0/24")
        return f"""! === CISCO: CONFIGURAÇÃO DE VLAN & TRUNK ===
enable
configure terminal

! 1. Criação da VLAN
vlan {vlan_id}
 name {vlan_name}
exit

! 2. Configuração de Porta de Acesso (Host)
interface {access_port}
 description Link para Host / Estacao
 switchport mode access
 switchport access vlan {vlan_id}
 spanning-tree portfast
 no shutdown
exit

! 3. Configuração de Porta Trunk (Uplink / Switch)
interface {trunk_port}
 description Trunk Uplink Switch/Router
 switchport trunk encapsulation dot1q
 switchport mode trunk
 switchport trunk allowed vlan add {vlan_id}
 no shutdown
end
write memory
"""

    elif t in ["stick", "router-on-a-stick"]:
        phys_int = params.get("interface", "GigabitEthernet0/0")
        return f"""! === CISCO: ROUTER-ON-A-STICK (INTER-VLAN ROUTING) ===
enable
configure terminal

! 1. Habilita interface física sem IP
interface {phys_int}
 no shutdown
exit

! 2. Subinterface VLAN 10
interface {phys_int}.10
 description Gateway VLAN 10 (Dados)
 encapsulation dot1Q 10
 ip address 192.168.10.1 255.255.255.0
 no shutdown
exit

! 3. Subinterface VLAN 20
interface {phys_int}.20
 description Gateway VLAN 20 (Voz/Wifi)
 encapsulation dot1Q 20
 ip address 192.168.20.1 255.255.255.0
 no shutdown
end
write memory
"""

    elif t in ["ospf"]:
        area = params.get("area", "0")
        proc_id = params.get("process", "1")
        return f"""! === CISCO: ROTEAMENTO DINÂMICO OSPFv2 ===
enable
configure terminal

router ospf {proc_id}
 router-id 1.1.1.1
 ! Divulga as redes internas na Área {area} (Backbone)
 network 192.168.10.0 0.0.0.255 area {area}
 network 192.168.20.0 0.0.0.255 area {area}
 network 10.0.0.0 0.0.0.3 area {area}
 passive-interface default
 no passive-interface GigabitEthernet0/0
 no shutdown
end
write memory
"""

    elif t in ["dhcp"]:
        pool_name = params.get("pool_name", "LAN_POOL")
        return f"""! === CISCO: SERVIDOR DHCP INTEGRADO ===
enable
configure terminal

! 1. Endereços reservados/excluídos (Gateways, Servidores, Impressoras)
ip dhcp excluded-address 192.168.10.1 192.168.10.20

! 2. Criação do Pool DHCP
ip dhcp pool {pool_name}
 network 192.168.10.0 255.255.255.0
 default-router 192.168.10.1
 dns-server 1.1.1.1 8.8.8.8
 domain-name hannya.local
 lease 7 0 0
end
write memory
"""

    elif t in ["nat", "pat"]:
        in_int = params.get("inside", "GigabitEthernet0/1")
        out_int = params.get("outside", "GigabitEthernet0/0")
        return f"""! === CISCO: NAT OVERLOAD (PAT - ACESSO À INTERNET) ===
enable
configure terminal

! 1. Definir interfaces Inside e Outside
interface {in_int}
 ip nat inside
exit

interface {out_int}
 ip nat outside
exit

! 2. ACL permitindo as redes internas
access-list 1 permit 192.168.10.0 0.0.0.255
access-list 1 permit 192.168.20.0 0.0.0.255

! 3. Regra de NAT com Sobrecarga na interface WAN
ip nat inside source list 1 interface {out_int} overload
end
write memory
"""
    else:
        return f"! Template '{template_type}' não reconhecido. Use: vlan, stick, ospf, dhcp, nat."


# ==========================================
# 🛡️ SEGURANÇA & AUDITORIA DE INFRAESTRUTURA
# ==========================================

async def audit_http_headers(url: str) -> dict:
    """Audita os cabeçalhos de segurança HTTP/HTTPS de um servidor e gera pontuação."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    try:
        timeout = aiohttp.ClientTimeout(total=6.0)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, allow_redirects=True, ssl=False) as resp:
                headers = {k.lower(): v for k, v in resp.headers.items()}
                score = 100
                checks = []

                # 1. HSTS
                if "strict-transport-security" in headers:
                    checks.append(("Strict-Transport-Security (HSTS)", True, "Protege contra downgrade de SSL/TLS."))
                else:
                    checks.append(("Strict-Transport-Security (HSTS)", False, "Ausente! Suscetível a ataques Man-in-the-Middle."))
                    score -= 25

                # 2. CSP
                if "content-security-policy" in headers:
                    checks.append(("Content-Security-Policy (CSP)", True, "Protege contra XSS e injeção de dados."))
                else:
                    checks.append(("Content-Security-Policy (CSP)", False, "Ausente! Risco de injeção de scripts (XSS)."))
                    score -= 25

                # 3. X-Frame-Options
                if "x-frame-options" in headers:
                    checks.append(("X-Frame-Options", True, f"Protege contra Clickjacking ({headers['x-frame-options']})."))
                else:
                    checks.append(("X-Frame-Options", False, "Ausente! Página vulnerável a Clickjacking."))
                    score -= 15

                # 4. X-Content-Type-Options
                if "x-content-type-options" in headers and "nosniff" in headers["x-content-type-options"].lower():
                    checks.append(("X-Content-Type-Options", True, "Evita sniffing de MIME types maliciosos."))
                else:
                    checks.append(("X-Content-Type-Options", False, "Ausente! Pode interpretar arquivos maliciosos."))
                    score -= 15

                # 5. Referrer-Policy
                if "referrer-policy" in headers:
                    checks.append(("Referrer-Policy", True, "Controle de vazamento de URL de origem."))
                else:
                    checks.append(("Referrer-Policy", False, "Ausente! URLs internas podem vazar em referrers."))
                    score -= 10

                # 6. Informações de Servidor expostas
                server_hdr = headers.get("server") or headers.get("x-powered-by")
                if server_hdr:
                    checks.append(("Informações de Servidor", False, f"Vazamento de tecnologia: '{server_hdr}'"))
                    score -= 10
                else:
                    checks.append(("Ocultação de Servidor", True, "Banner de servidor protegido ou ausente."))

                score = max(0, score)
                if score >= 90:
                    grade = "A+"
                elif score >= 80:
                    grade = "A"
                elif score >= 65:
                    grade = "B"
                elif score >= 50:
                    grade = "C"
                elif score >= 35:
                    grade = "D"
                else:
                    grade = "F (Crítico)"

                return {
                    "success": True,
                    "url": str(resp.url),
                    "status_code": resp.status,
                    "score": score,
                    "grade": grade,
                    "checks": checks
                }
    except Exception as e:
        return {"success": False, "error": f"Falha ao conectar no host: {e}"}


DNSBL_SERVERS = [
    ("zen.spamhaus.org", "Spamhaus ZEN"),
    ("bl.spamcop.net", "SpamCop"),
    ("b.barracudacentral.org", "Barracuda"),
    ("dnsbl.sorbs.net", "SORBS"),
    ("dnsbl-1.uceprotect.net", "UCEPROTECT-Level1")
]


async def check_dnsbl_blacklist(ip_str: str) -> list[dict]:
    """Verifica se um endereço IPv4 está listado em DNSBLs de spam e malware."""
    clean_ip = ip_str.strip()
    try:
        ipaddress.IPv4Address(clean_ip)
    except ValueError:
        return [{"server": "Erro", "listed": False, "error": "Informe um endereço IPv4 válido."}]

    reversed_ip = ".".join(reversed(clean_ip.split(".")))
    resolver = dns.resolver.Resolver()
    resolver.timeout = 2.0
    resolver.lifetime = 2.0

    async def check_single(dnsbl_host: str, name: str):
        query_host = f"{reversed_ip}.{dnsbl_host}"
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, resolver.resolve, query_host, "A")
            return {"server": name, "host": dnsbl_host, "listed": True}
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return {"server": name, "host": dnsbl_host, "listed": False}
        except Exception:
            return {"server": name, "host": dnsbl_host, "listed": False, "note": "Sem resposta"}

    tasks = [check_single(host, name) for host, name in DNSBL_SERVERS]
    return await asyncio.gather(*tasks)


def check_dnssec(domain: str) -> dict:
    """Verifica se o domínio possui DNSSEC configurado e ativo."""
    clean_domain = domain.replace("http://", "").replace("https://", "").split("/")[0].strip()
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3.0
    resolver.lifetime = 3.0

    has_dnskey = False
    has_ds = False

    try:
        resolver.resolve(clean_domain, "DNSKEY")
        has_dnskey = True
    except Exception:
        pass

    try:
        resolver.resolve(clean_domain, "DS")
        has_ds = True
    except Exception:
        pass

    is_secure = has_dnskey and has_ds
    return {
        "domain": clean_domain,
        "has_dnskey": has_dnskey,
        "has_ds": has_ds,
        "status": "Protegido por DNSSEC (Criptografia Ativa)" if is_secure else ("Parcial / Sem chave DS" if has_dnskey else "Inativo (Vulnerável a DNS Spoofing)")
    }


# ==========================================
# 📊 GRÁFICOS VISUAIS DE LATÊNCIA (MATPLOTLIB)
# ==========================================

def generate_latency_chart(host_name: str, history_rows: list) -> bytes:
    """Gera um gráfico visual de histórico de latência com visual cyberpunk Hannya."""
    import io
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if not history_rows:
        timestamps = ["00:00"]
        latencies = [0.0]
    else:
        timestamps = [row["timestamp"] for row in history_rows]
        latencies = [row["latency_ms"] for row in history_rows]

    fig, ax = plt.subplots(figsize=(8, 4), dpi=130)

    # Cores Hannya: Fundo escuro, linha ciano vibrante
    fig.patch.set_facecolor("#0F111A")
    ax.set_facecolor("#1A1C29")

    # Linha principal com brilho
    ax.plot(timestamps, latencies, color="#00F0FF", linewidth=2.5, marker="o", markersize=4, label="Latência (ms)")
    ax.fill_between(timestamps, latencies, color="#00F0FF", alpha=0.15)

    # Grid e eixos
    ax.grid(True, linestyle="--", alpha=0.25, color="#8F93A2")
    ax.tick_params(colors="#C3C7DB", labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#2D3142")

    # Títulos e labels
    ax.set_title(f"⚡ Histórico de Latência — {host_name}", color="#FFFFFF", fontsize=11, fontweight="bold", pad=12)
    ax.set_ylabel("Tempo de Resposta (ms)", color="#8F93A2", fontsize=9)
    ax.legend(facecolor="#1A1C29", edgecolor="#2D3142", labelcolor="#FFFFFF", fontsize=8)

    # Ajusta rotação das horas se forem muitos pontos
    if len(timestamps) > 8:
        plt.xticks(rotation=45)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
