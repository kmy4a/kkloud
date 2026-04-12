import yaml
import uuid
from ..model.vpc_models import VPC, RequestVPC
from ..infrastructure import vpc_infrastructure as vpcs_infra


class VPCs:
    def __init__(self, data_file="data/vpc_repository.yml"):
        """Initialize the VPCs service with the specified data file."""
        self._data_file: str = data_file
        self.vpcs: list[VPC] = self._load()

    def _load(self) -> list[VPC]:
        """Load VPCs from the YAML file."""
        with open(self._data_file, "r") as file:
            data = yaml.safe_load(file)
            return [VPC(**vpc) for vpc in data.get("vpcs", [])]

    def _save(self) -> None:
        """Save the current list of VPCs to the YAML file."""
        with open(self._data_file, "w") as file:
            yaml.dump({"vpcs": [vpc.model_dump() for vpc in self.vpcs]}, file)

    def get_all(self) -> list[VPC]:
        """Return a list of all VPCs."""
        return self.vpcs

    def get(self, vpc_id: str) -> VPC:
        """Return a VPC by its ID.

        Raises:
            ValueError: If the VPC with the specified ID is not found.
        """
        vpc = next((vpc for vpc in self.vpcs if vpc.id == vpc_id), None)
        if not vpc:
            raise ValueError(f"VPC with id {vpc_id} not found")
        return vpc

    def add(self, request_vpc: RequestVPC) -> str:
        """Add a new VPC based on the provided request data.

        Returns:
            vpc_id (str): The ID of the newly created VPC.
        Raises:
            RuntimeError: If the VPC creation fails.
        """
        vpc_obj = VPC(
            id="vpc-" + str(uuid.uuid4()),
            name=request_vpc.name,
            cidr_block=request_vpc.cidr_block,
            vni=self.vpcs.__len__() + 1000,
            is_attatched_to_igw=False,
        )

        try:
            vpcs_infra.create_vpc(vpc_obj)
        except RuntimeError:
            raise RuntimeError(f"Failed to create VPC with id {vpc_obj.id}")

        self.vpcs.append(vpc_obj)
        self._save()
        return vpc_obj.id

    def delete(self, vpc_id: str) -> None:
        """Delete a VPC by its ID.

        Raises:
            ValueError: If the VPC with the specified ID is not found.
        """
        if not any(vpc.id == vpc_id for vpc in self.vpcs):
            raise ValueError(f"VPC with id {vpc_id} not found")

        vpc = VPC(
            id=vpc_id,
            name=next(vpc.name for vpc in self.vpcs if vpc.id == vpc_id),
            cidr_block=next(
                vpc.cidr_block for vpc in self.vpcs if vpc.id == vpc_id
            ),
            vni=int(next(vpc.vni for vpc in self.vpcs if vpc.id == vpc_id)),
            is_attatched_to_igw=bool(
                next(
                    vpc.is_attatched_to_igw
                    for vpc in self.vpcs
                    if vpc.id == vpc_id
                )
            ),
        )

        try:
            vpcs_infra.delete_vpc(vpc)
        except RuntimeError:
            raise RuntimeError(f"Failed to delete VPC with id {vpc_id}")

        self.vpcs = [vpc for vpc in self.vpcs if vpc.id != vpc_id]
        self._save()

    def attach_igw(self, vpc_id: str) -> None:
        """Attach an Internet Gateway (IGW) to a VPC.

        Raises:
            RuntimeError: If the VPC is already attached to an IGW.
        """
        vpc = self.get(vpc_id)
        if vpc.is_attatched_to_igw:
            raise RuntimeError(f"VPC with id {vpc_id} is already attached to IGW")

        vpc_obj = VPC(
            id=vpc_id,
            name=vpc.name,
            cidr_block=vpc.cidr_block,
            vni=vpc.vni,
            is_attatched_to_igw=True,
        )

        try:
            vpcs_infra.attach_igw(vpc_obj)
        except RuntimeError:
            raise RuntimeError(f"Failed to attach IGW to VPC with id {vpc_id}")

        self.vpcs = [
            v if v.id != vpc_id else vpc_obj for v in self.vpcs
        ]
        self._save()

    def detach_igw(self, vpc_id: str) -> None:
        """Detach an Internet Gateway (IGW) from a VPC.

        Raises:
            RuntimeError: If the VPC is not attached to an IGW.
        """
        vpc = self.get(vpc_id)
        if not vpc.is_attatched_to_igw:
            raise RuntimeError(f"VPC with id {vpc_id} is not attached to IGW")

        vpc_obj = VPC(
            id=vpc_id,
            name=vpc.name,
            cidr_block=vpc.cidr_block,
            vni=vpc.vni,
            is_attatched_to_igw=False,
        )

        try:
            vpcs_infra.detach_igw(vpc_obj)
        except RuntimeError:
            raise RuntimeError(f"Failed to detach IGW from VPC with id {vpc_id}")

        self.vpcs = [
            v if v.id != vpc_id else vpc_obj for v in self.vpcs
        ]
        self._save()


vpcs = VPCs()
