import yaml
from ..model.vpc_models import VPC


class VPCLoader:
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

    def add(self, vpc: VPC) -> None:
        """Add a new VPC to the list and save it to the YAML file."""
        self.vpcs.append(vpc)
        self._save()

    def delete(self, vpc_id: str) -> None:
        """Delete a VPC by its ID and save the updated list to the YAML file."""
        self.vpcs = [vpc for vpc in self.vpcs if vpc.id != vpc_id]
        self._save()

    def update(self, vpc: VPC) -> None:
        """Update an existing VPC and save the updated list to the YAML file."""
        self.vpcs = [v if v.id != vpc.id else vpc for v in self.vpcs]
        self._save()


vpc_loader = VPCLoader()
