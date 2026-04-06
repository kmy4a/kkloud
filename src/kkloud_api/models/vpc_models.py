from pydantic import BaseModel
from ipaddress import IPv4Network


class RequestVPC(BaseModel):
    name: str
    cidr_block: IPv4Network


class VPC(BaseModel):
    id: str
    name: str
    cidr_block: str
    vni: int
    is_attatched_to_igw: bool