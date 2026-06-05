import paydunya
from django.conf import settings

cfg = settings.PAYDUNYA

paydunya.api_keys = {
    "PAYDUNYA-MASTER-KEY": cfg["MASTER_KEY"],
    "PAYDUNYA-PRIVATE-KEY": cfg["PRIVATE_KEY"],
    "PAYDUNYA-TOKEN": cfg["TOKEN"],
}

paydunya.debug = cfg["MODE"] == "test"

store = paydunya.Store(
    name=cfg["STORE_NAME"],
    tagline=cfg["STORE_TAGLINE"],
    cancel_url=cfg["CANCEL_URL"],
    return_url=cfg["RETURN_URL"],
    callback_url=cfg["CALLBACK_URL"],
)


def creer_facture(
    montant: int,
    description: str,
    parent_nom: str,
    parent_email: str,
    parent_phone: str,
    **custom_data,
) -> tuple[bool, dict]:
    invoice = paydunya.Invoice(store)
    invoice.total_amount = montant
    invoice.description = description
    invoice.customer = {
        "name": parent_nom,
        "phone": parent_phone,
        "email": parent_email,
    }
    if custom_data:
        invoice.add_custom_data(list(custom_data.items()))
    return invoice.create()


def confirmer_paiement(token: str) -> tuple[bool, dict]:
    invoice = paydunya.Invoice(store)
    return invoice.confirm(token)
