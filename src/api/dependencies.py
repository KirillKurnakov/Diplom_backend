from utils.unitofwork import UnitOfWork, IUnitOfWork
from fastapi import Depends
from typing import Annotated


def uow_dependency() -> IUnitOfWork:
    return UnitOfWork()


UOWDep = Annotated[IUnitOfWork, Depends(uow_dependency)]
