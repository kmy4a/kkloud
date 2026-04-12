from pydantic import BaseModel
from ipaddress import IPv4Network


class RequestVPC(BaseModel):
    name: str
    cidr_block: IPv4Network


class VPC(RequestVPC):
    id: str
    name: str
    cidr_block: IPv4Network
    vni: int
    is_attatched_to_igw: bool
