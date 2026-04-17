from fastapi import APIRouter
from fastapi import HTTPException
from ..service.vpc_service import vpcs
from ..service.subnet_service import subnets
from ..service.fabric_service import fabrics
from ..model.vpc_models import RequestVPC
from ..model.subnet_models import RequestSubnet
from ..exceptions import (
    VPCNotFoundError,
    VPCDeletionError,
    SubnetInvalidCIDRError,
    SubnetNotFoundError,
)


router = APIRouter(prefix="/api/v1", tags=["VPCs API"])


@router.get("/api_health")
async def get_status():
    return {"is_healthy": True}


@router.get("/fabric_health")
async def get_fabric_health():
    try:
        fabrics.health_check()
        return {"is_healthy": True}
    except RuntimeError:
        return {"is_healthy": False}


@router.get("/vpcs")
async def get_vpcs():
    return {"vpcs": vpcs.get_all()}


@router.post("/vpcs", status_code=201)
async def create_vpc(vpc: RequestVPC):
    try:
        id: str = await vpcs.add(vpc)
        return {"message": "VPC created successfully", "vpc_id": id}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/vpcs/{vpc_id}", status_code=204)
async def delete_vpc(vpc_id: str):
    try:
        await vpcs.delete(vpc_id)
        return {"message": f"VPC {vpc_id} deleted successfully"}
    except VPCNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except VPCDeletionError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vpcs/{vpc_id}/subnets")
async def get_subnets(vpc_id: str):
    return {"subnets": subnets.get_all(vpc_id)}


@router.post("/vpcs/{vpc_id}/subnets", status_code=201)
async def create_subnet(vpc_id: str, request_subnet: RequestSubnet):
    try:
        id: str = subnets.add(vpc_id, request_subnet)
        return {"message": "Subnet created successfully", "subnet_id": id}
    except VPCNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except SubnetInvalidCIDRError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/vpcs/{vpc_id}/subnets/{subnet_id}", status_code=204)
async def delete_subnet(vpc_id: str, subnet_id: str):
    try:
        subnets.delete(vpc_id, subnet_id)
        return {"message": f"Subnet {subnet_id} deleted successfully"}
    except (VPCNotFoundError, SubnetNotFoundError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vpcs/{vpc_id}/igw")
async def get_igw_states(vpc_id: str):
    vpc = vpcs.get(vpc_id)
    return {"is_attached": vpc.is_attached_to_igw}


@router.post("/vpcs/{vpc_id}/igw", status_code=201)
async def attach_igw(vpc_id: str):
    try:
        await vpcs.attach_igw(vpc_id)
        return {"message": f"IGW attached to VPC {vpc_id} successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/vpcs/{vpc_id}/igw", status_code=204)
async def detach_igw(vpc_id: str):
    try:
        await vpcs.detach_igw(vpc_id)
        return {"message": f"IGW detached from VPC {vpc_id} successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
