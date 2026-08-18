from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from server import get_db
from settings.database import (
    AssetCreate,
    AssetResponse,
    AssetUpdate,
    ControlCreate,
    ControlResponse,
    ControlUpdate,
    HealthResponse,
    RiskCreate,
    RiskResponse,
    RiskUpdate,
    SettingsResponse,
    TreatmentActionCreate,
    TreatmentActionResponse,
    TreatmentActionUpdate,
)
from settings.models import Asset, Control, Risk, TreatmentAction

api_router = APIRouter()


# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------

@api_router.get("/health", tags=["System"], response_model=HealthResponse)
def health_check():
    return {
        "status": "healthy",
        "database": "Oracle Database",
    }


@api_router.get("/settings", tags=["Settings"], response_model=SettingsResponse)
def get_settings():
    return {
        "application": "RiskPilot",
        "version": "0.1.0",
    }


# ---------------------------------------------------------------------------
# Assets
# ---------------------------------------------------------------------------

@api_router.get("/assets", tags=["Assets"], response_model=list[AssetResponse])
def list_assets(db: Session = Depends(get_db)):
    return db.query(Asset).order_by(Asset.id).all()


@api_router.get("/assets/{asset_id}", tags=["Assets"], response_model=AssetResponse)
def get_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.get(Asset, asset_id)

    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ativo não encontrado.")

    return asset


@api_router.post(
    "/assets",
    tags=["Assets"],
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_asset(payload: AssetCreate, db: Session = Depends(get_db)):
    asset = Asset(
        name=payload.name,
        description=payload.description,
        classification=payload.classification.value,
        asset_type=payload.asset_type.value,
        owner=payload.owner,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@api_router.put("/assets/{asset_id}", tags=["Assets"], response_model=AssetResponse)
def update_asset(asset_id: int, payload: AssetUpdate, db: Session = Depends(get_db)):
    asset = db.get(Asset, asset_id)

    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ativo não encontrado.")

    updates = payload.model_dump(exclude_unset=True)

    if "classification" in updates:
        updates["classification"] = updates["classification"].value
    if "asset_type" in updates:
        updates["asset_type"] = updates["asset_type"].value

    for field, value in updates.items():
        setattr(asset, field, value)

    db.commit()
    db.refresh(asset)
    return asset


@api_router.delete("/assets/{asset_id}", tags=["Assets"], status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    asset = db.get(Asset, asset_id)

    if asset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ativo não encontrado.")

    db.delete(asset)
    db.commit()


# ---------------------------------------------------------------------------
# Risks
# ---------------------------------------------------------------------------

@api_router.get("/risks", tags=["Risks"], response_model=list[RiskResponse])
def list_risks(db: Session = Depends(get_db)):
    return db.query(Risk).order_by(Risk.id).all()


@api_router.get("/risks/{risk_id}", tags=["Risks"], response_model=RiskResponse)
def get_risk(risk_id: int, db: Session = Depends(get_db)):
    risk = db.get(Risk, risk_id)

    if risk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risco não encontrado.")

    return risk


@api_router.post(
    "/risks",
    tags=["Risks"],
    response_model=RiskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_risk(payload: RiskCreate, db: Session = Depends(get_db)):
    if payload.asset_id is not None and db.get(Asset, payload.asset_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ativo não encontrado.")

    risk_level, risk_score = Risk.compute_levels(payload.likelihood, payload.impact)
    risk = Risk(
        title=payload.title,
        description=payload.description,
        asset_id=payload.asset_id,
        likelihood=payload.likelihood,
        impact=payload.impact,
        risk_level=risk_level,
        risk_score=risk_score,
        status=payload.status.value,
    )
    db.add(risk)
    db.commit()
    db.refresh(risk)
    return risk


@api_router.put("/risks/{risk_id}", tags=["Risks"], response_model=RiskResponse)
def update_risk(risk_id: int, payload: RiskUpdate, db: Session = Depends(get_db)):
    risk = db.get(Risk, risk_id)

    if risk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risco não encontrado.")

    updates = payload.model_dump(exclude_unset=True)

    if "asset_id" in updates and updates["asset_id"] is not None:
        if db.get(Asset, updates["asset_id"]) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ativo não encontrado.")

    if "status" in updates:
        updates["status"] = updates["status"].value

    for field, value in updates.items():
        setattr(risk, field, value)

    risk_level, risk_score = Risk.compute_levels(risk.likelihood, risk.impact)
    risk.risk_level = risk_level
    risk.risk_score = risk_score

    db.commit()
    db.refresh(risk)
    return risk


@api_router.delete("/risks/{risk_id}", tags=["Risks"], status_code=status.HTTP_204_NO_CONTENT)
def delete_risk(risk_id: int, db: Session = Depends(get_db)):
    risk = db.get(Risk, risk_id)

    if risk is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risco não encontrado.")

    db.delete(risk)
    db.commit()


# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------

@api_router.get("/controls", tags=["Controls"], response_model=list[ControlResponse])
def list_controls(db: Session = Depends(get_db)):
    return db.query(Control).order_by(Control.id).all()


@api_router.get("/controls/{control_id}", tags=["Controls"], response_model=ControlResponse)
def get_control(control_id: int, db: Session = Depends(get_db)):
    control = db.get(Control, control_id)

    if control is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Controlo não encontrado.")

    return control


@api_router.post(
    "/controls",
    tags=["Controls"],
    response_model=ControlResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_control(payload: ControlCreate, db: Session = Depends(get_db)):
    if payload.risk_id is not None and db.get(Risk, payload.risk_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risco não encontrado.")

    control = Control(
        name=payload.name,
        description=payload.description,
        risk_id=payload.risk_id,
        control_type=payload.control_type.value,
        implementation_status=payload.implementation_status.value,
        framework_reference=payload.framework_reference,
    )
    db.add(control)
    db.commit()
    db.refresh(control)
    return control


@api_router.put("/controls/{control_id}", tags=["Controls"], response_model=ControlResponse)
def update_control(control_id: int, payload: ControlUpdate, db: Session = Depends(get_db)):
    control = db.get(Control, control_id)

    if control is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Controlo não encontrado.")

    updates = payload.model_dump(exclude_unset=True)

    if "risk_id" in updates and updates["risk_id"] is not None:
        if db.get(Risk, updates["risk_id"]) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risco não encontrado.")

    if "control_type" in updates:
        updates["control_type"] = updates["control_type"].value
    if "implementation_status" in updates:
        updates["implementation_status"] = updates["implementation_status"].value

    for field, value in updates.items():
        setattr(control, field, value)

    db.commit()
    db.refresh(control)
    return control


@api_router.delete("/controls/{control_id}", tags=["Controls"], status_code=status.HTTP_204_NO_CONTENT)
def delete_control(control_id: int, db: Session = Depends(get_db)):
    control = db.get(Control, control_id)

    if control is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Controlo não encontrado.")

    db.delete(control)
    db.commit()


# ---------------------------------------------------------------------------
# Treatment actions
# ---------------------------------------------------------------------------

@api_router.get(
    "/treatment-actions",
    tags=["Treatment Actions"],
    response_model=list[TreatmentActionResponse],
)
def list_treatment_actions(db: Session = Depends(get_db)):
    return db.query(TreatmentAction).order_by(TreatmentAction.id).all()


@api_router.get(
    "/treatment-actions/{action_id}",
    tags=["Treatment Actions"],
    response_model=TreatmentActionResponse,
)
def get_treatment_action(action_id: int, db: Session = Depends(get_db)):
    action = db.get(TreatmentAction, action_id)

    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ação de tratamento não encontrada.",
        )

    return action


@api_router.post(
    "/treatment-actions",
    tags=["Treatment Actions"],
    response_model=TreatmentActionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_treatment_action(payload: TreatmentActionCreate, db: Session = Depends(get_db)):
    if db.get(Risk, payload.risk_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Risco não encontrado.")

    action = TreatmentAction(
        risk_id=payload.risk_id,
        title=payload.title,
        description=payload.description,
        owner=payload.owner,
        due_date=payload.due_date,
        treatment_type=payload.treatment_type.value,
        status=payload.status.value,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


@api_router.put(
    "/treatment-actions/{action_id}",
    tags=["Treatment Actions"],
    response_model=TreatmentActionResponse,
)
def update_treatment_action(
    action_id: int,
    payload: TreatmentActionUpdate,
    db: Session = Depends(get_db),
):
    action = db.get(TreatmentAction, action_id)

    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ação de tratamento não encontrada.",
        )

    updates = payload.model_dump(exclude_unset=True)

    if "treatment_type" in updates:
        updates["treatment_type"] = updates["treatment_type"].value
    if "status" in updates:
        updates["status"] = updates["status"].value

    for field, value in updates.items():
        setattr(action, field, value)

    db.commit()
    db.refresh(action)
    return action


@api_router.delete(
    "/treatment-actions/{action_id}",
    tags=["Treatment Actions"],
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_treatment_action(action_id: int, db: Session = Depends(get_db)):
    action = db.get(TreatmentAction, action_id)

    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ação de tratamento não encontrada.",
        )

    db.delete(action)
    db.commit()
