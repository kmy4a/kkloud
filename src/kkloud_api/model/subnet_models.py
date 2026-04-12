from pydantic import BaseModel
from ipaddress import IPv4Network


class RequestSubnet(BaseModel):
    name: str
    cidr_block: IPv4Network


class Subnet(RequestSubnet):
    id: str
    vpc_id: str
    name: str
    cidr_block: IPv4Network
    vni: int
