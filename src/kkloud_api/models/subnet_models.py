from pydantic import BaseModel
from ipaddress import IPv4Network


class RequestSubnet(BaseModel):
    name: str
    cidr_block: IPv4Network


class Subnet(BaseModel):
    id: str
    vpc_id: str
    name: str
    cidr_block: str
    vni: int
