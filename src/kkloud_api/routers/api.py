from fastapi import APIRouter
from fastapi import HTTPException
from ..domain.vpc_service import vpcs
from ..domain.subnet_service import subnets
from ..infrastructure import fabric_infrastructure as fabric_infra
from ..models.vpc_models import RequestVPC
from ..models.subnet_models import RequestSubnet


router = APIRouter(prefix="/api/v1", tags=["VPCs API"])


@router.get("/api_health")
async def get_status():
    return {"is_alive": True}


@router.get("/fabric_health")
async def get_fabric_status():
    try:
        fabric_infra.ping_to_fabric()
        return {"is_alive": True}
    except RuntimeError:
        return {"is_alive": False}


@router.get("/vpcs")
async def get_vpcs():
    return {"vpcs": vpcs.get_all()}


@router.post("/vpcs", status_code=201)
async def create_vpc(vpc: RequestVPC):
    try:
        id: str = vpcs.add(vpc)
        return {"message": "VPC created successfully", "vpc_id": id}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/vpcs/{vpc_id}")
async def delete_vpc(vpc_id: str):
    try:
        vpcs.delete(vpc_id)
        return {"message": f"VPC {vpc_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vpcs/{vpc_id}/subnets")
async def get_subnets(vpc_id: str):
    return {"subnets": subnets.get_all(vpc_id)}


@router.post("/vpcs/{vpc_id}/subnets")
async def create_subnet(vpc_id: str, request_subnet: RequestSubnet):
    try:
        id: str = subnets.add(vpc_id, request_subnet)
        return {"message": "Subnet created successfully", "subnet_id": id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/vpcs/{vpc_id}/subnets/{subnet_id}")
async def delete_subnet(vpc_id: str, subnet_id: str):
    try:
        subnets.delete(vpc_id, subnet_id)
        return {"message": f"Subnet {subnet_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vpcs/{vpc_id}/igw")
async def get_igw_states(vpc_id: str):
    vpc = vpcs.get(vpc_id)
    return {"is_attached": vpc["is_attatched_to_igw"]}


@router.post("/vpcs/{vpc_id}/igw")
async def attach_igw(vpc_id: str):
    try:
        vpcs.attach_igw(vpc_id)
        return {"message": f"IGW attached to VPC {vpc_id} successfully"}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/vpcs/{vpc_id}/igw")
async def detach_igw(vpc_id: str):
    try:
        vpcs.detach_igw(vpc_id)
        return {"message": f"IGW detached from VPC {vpc_id} successfully"}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
