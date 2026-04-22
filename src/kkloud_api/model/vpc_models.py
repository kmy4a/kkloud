from pydantic import BaseModel, field_validator, field_serializer
from ipaddress import IPv4Network


class RequestVPC(BaseModel):
    name: str
    cidr_block: IPv4Network


class VPC(RequestVPC):
    id: str
    vni: int
    is_attached_to_igw: bool

    @field_serializer("cidr_block")
    def serialize_cidr(self, v: IPv4Network):
        return str(v)

    @field_validator("cidr_block", mode="before")
    def parse_cidr(cls, v):
        if isinstance(v, str):
            return IPv4Network(v)
        return v
