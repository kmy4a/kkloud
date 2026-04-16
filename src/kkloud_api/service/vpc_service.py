import uuid
from ..model.vpc_models import VPC, RequestVPC
from ..infrastructure import vpc_runner as vpcs_infra
from ..infrastructure.vpc_loader import vpc_loader
from ..infrastructure.subnet_loader import subnet_loader
from ..infrastructure.logger import logger
from ..exceptions import VPCNotFoundError, VPCDeletionError


class VPCs:
    def __init__(self):
        """Initialize the VPCs service with the specified data file."""
        self.vpc_loader = vpc_loader
        self.subnet_loader = subnet_loader
        self.logger = logger

    def get_all(self) -> list[VPC]:
        """Return a list of all VPCs."""
        return self.vpc_loader.vpcs

    def get(self, vpc_id: str) -> VPC:
        """Return a VPC by its ID.

        Raises:
            VPCNotFoundError: If the VPC with the specified ID is not found.
        """
        for vpc in self.vpc_loader.vpcs:
            if vpc.id == vpc_id:
                return vpc
        raise VPCNotFoundError(f"VPC with id {vpc_id} not found")

    async def add(self, request_vpc: RequestVPC) -> str:
        """Add a new VPC based on the provided request data.

        Returns:
            vpc_id (str): The ID of the newly created VPC.
        Raises:
            RuntimeError: If the VPC creation fails.
        """
        vpc = VPC(
            id=f"vpc-{uuid.uuid4()}",
            name=request_vpc.name,
            cidr_block=request_vpc.cidr_block,
            vni=1
            if len(self.vpc_loader.vpcs) == 0
            else len(self.vpc_loader.vpcs) * 1000,
            is_attached_to_igw=False,
        )

        try:
            await vpcs_infra.create_vpc(vpc)
        except RuntimeError:
            raise RuntimeError(f"Failed to create VPC with id {vpc.id}")

        self.vpc_loader.add(vpc)
        self.logger.info(f"Created VPC with id {vpc.id}")
        return vpc.id

    async def delete(self, vpc_id: str) -> None:
        """Delete a VPC by its ID.

        Raises:
            VPCNotFoundError: If the VPC with the specified ID is not found.
            VPCDeletionError: If the VPC have associated subnet.
            RuntimeError: If the VPC deletion fails.
        """
        vpc = None
        for v in self.vpc_loader.vpcs:
            if v.id == vpc_id:
                vpc = v
                break

        if vpc is None:
            raise VPCNotFoundError(f"VPC with id {vpc_id} not found")

        subnets_in_vpc = [
            subnet for subnet in self.subnet_loader.subnets if subnet.vpc_id == vpc_id
        ]
        if subnets_in_vpc:
            raise VPCDeletionError(
                f"Cannot delete VPC with id {vpc_id} because it has associated subnets. Please delete the subnets first."
            )

        try:
            await vpcs_infra.delete_vpc(vpc)
        except RuntimeError:
            raise RuntimeError(f"Failed to delete VPC with id {vpc_id}")

        self.vpc_loader.delete(vpc_id)
        self.logger.info(f"Deleted VPC with id {vpc.id}")

    async def attach_igw(self, vpc_id: str) -> None:
        """Attach an Internet Gateway (IGW) to a VPC.

        Raises:
            ValueError: If the VPC is already attached to an IGW.
            RuntimeError: If the IGW attach fails.
        """
        vpc = self.get(vpc_id)
        if vpc.is_attached_to_igw:
            raise ValueError(f"VPC with id {vpc_id} is already attached to IGW")

        try:
            await vpcs_infra.attach_igw(vpc)
        except RuntimeError:
            raise RuntimeError(f"Failed to attach IGW to VPC with id {vpc_id}")

        vpc.is_attached_to_igw = True
        self.vpc_loader.update(vpc)
        self.logger.info(f"Attached IGW to VPC with id {vpc.id}")

    async def detach_igw(self, vpc_id: str) -> None:
        """Detach an Internet Gateway (IGW) from a VPC.

        Raises:
            ValueError: If the VPC is not attached to an IGW.
            RuntimeError: If the IGW attach fails.
        """
        vpc = self.get(vpc_id)
        if not vpc.is_attached_to_igw:
            raise ValueError(f"VPC with id {vpc_id} is not attached to IGW")

        try:
            await vpcs_infra.detach_igw(vpc)
        except RuntimeError:
            raise RuntimeError(f"Failed to detach IGW from VPC with id {vpc_id}")

        vpc.is_attached_to_igw = False
        self.vpc_loader.update(vpc)
        self.logger.info(f"Detached IGW from VPC with id {vpc.id}")


vpcs = VPCs()
