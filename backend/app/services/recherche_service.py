"""Recherche unifiée député / groupe / scrutin par texte libre."""

from sqlalchemy.orm import Session

from backend.app.models import Depute, Groupe, Scrutin
from backend.app.schemas.depute import DeputeOut
from backend.app.schemas.groupe import GroupeOut
from backend.app.schemas.recherche import RechercheResultat
from backend.app.schemas.scrutin import ScrutinOut

LIMITE_PAR_TYPE = 10


def rechercher(db: Session, q: str) -> RechercheResultat:
    """Recherche `q` dans le nom des députés, le nom des groupes et le titre des scrutins."""
    motif = f"%{q}%"

    deputes = (
        db.query(Depute)
        .filter((Depute.nom.ilike(motif)) | (Depute.prenom.ilike(motif)))
        .limit(LIMITE_PAR_TYPE)
        .all()
    )
    groupes = db.query(Groupe).filter(Groupe.nom.ilike(motif)).limit(LIMITE_PAR_TYPE).all()
    scrutins = db.query(Scrutin).filter(Scrutin.titre.ilike(motif)).limit(LIMITE_PAR_TYPE).all()

    return RechercheResultat(
        deputes=[DeputeOut.model_validate(d) for d in deputes],
        groupes=[GroupeOut.model_validate(g) for g in groupes],
        scrutins=[ScrutinOut.model_validate(s) for s in scrutins],
    )
