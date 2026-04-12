import yaml
import uuid
from ..models.vpc_models import VPC, RequestVPC
from ..infrastructure import vpc_infrastructure as vpcs_infra


class VPCs:
    def __init__(self, data_file="data/vpc_repository.yml"):
        self.data_file = data_file
        self.vpcs = self.load()

    def load(self) -> list[dict[str, str]]:
        with open(self.data_file, "r") as file:
            data = yaml.safe_load(file)
            return data.get("vpcs", [])

    def save(self) -> None:
        with open(self.data_file, "w") as file:
            yaml.dump({"vpcs": self.vpcs}, file)

    def get_all(self) -> list[dict[str, str]]:
        return self.vpcs

    def get(self, vpc_id: str) -> dict[str, str]:
        vpc = next((vpc for vpc in self.vpcs if vpc["id"] == vpc_id), None)
        if not vpc:
            raise ValueError(f"VPC with id {vpc_id} not found")
        return vpc

    def add(self, request_vpc: RequestVPC) -> str:
        vpc_obj = VPC(
            id="vpc-" + str(uuid.uuid4()),
            name=str(request_vpc.name),
            cidr_block=str(request_vpc.cidr_block),
            vni=self.vpcs.__len__() + 1000,
            is_attatched_to_igw=False,
        )
        vpcs_infra.create_vpc(vpc_obj)
        self.vpcs.append(vpc_obj.model_dump())
        self.save()
        return vpc_obj.id

    def delete(self, vpc_id: str) -> None:
        if not any(vpc["id"] == vpc_id for vpc in self.vpcs):
            raise ValueError(f"VPC with id {vpc_id} not found")
        vpc = VPC(
            id=vpc_id,
            name=next(vpc["name"] for vpc in self.vpcs if vpc["id"] == vpc_id),
            cidr_block=next(
                vpc["cidr_block"] for vpc in self.vpcs if vpc["id"] == vpc_id
            ),
            vni=int(next(vpc["vni"] for vpc in self.vpcs if vpc["id"] == vpc_id)),
            is_attatched_to_igw=bool(
                next(
                    vpc["is_attatched_to_igw"]
                    for vpc in self.vpcs
                    if vpc["id"] == vpc_id
                )
            ),
        )
        vpcs_infra.delete_vpc(vpc)
        self.vpcs = [vpc for vpc in self.vpcs if vpc["id"] != vpc_id]
        self.save()

    def attach_igw(self, vpc_id: str) -> None:
        vpc = self.get(vpc_id)
        if vpc["is_attatched_to_igw"]:
            raise RuntimeError(f"VPC with id {vpc_id} is already attached to IGW")
        vpc_obj = VPC(
            id=vpc_id,
            name=vpc["name"],
            cidr_block=vpc["cidr_block"],
            vni=int(vpc["vni"]),
            is_attatched_to_igw=True,
        )
        vpcs_infra.attach_igw(vpc_obj)
        self.vpcs = [
            v if v["id"] != vpc_id else vpc_obj.model_dump() for v in self.vpcs
        ]
        self.save()

    def detach_igw(self, vpc_id: str) -> None:
        vpc = self.get(vpc_id)
        if not vpc["is_attatched_to_igw"]:
            raise RuntimeError(f"VPC with id {vpc_id} is not attached to IGW")
        vpc_obj = VPC(
            id=vpc_id,
            name=vpc["name"],
            cidr_block=vpc["cidr_block"],
            vni=int(vpc["vni"]),
            is_attatched_to_igw=False,
        )
        vpcs_infra.detach_igw(vpc_obj)
        self.vpcs = [
            v if v["id"] != vpc_id else vpc_obj.model_dump() for v in self.vpcs
        ]
        self.save()


vpcs = VPCs()
