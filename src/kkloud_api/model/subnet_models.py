from pydantic import BaseModel, field_validator, field_serializer
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

    @field_serializer("cidr_block")
    def serialize_cidr(self, v: IPv4Network):
        return str(v)

    @field_validator("cidr_block", mode="before")
    def parse_cidr(cls, v):
        if isinstance(v, str):
            return IPv4Network(v)
        return v
