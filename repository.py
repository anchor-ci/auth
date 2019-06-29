from dataclasses import dataclass

@dataclass
class ProxyRequest:
    provider: str
    endpoint: str
    user: str
