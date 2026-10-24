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
