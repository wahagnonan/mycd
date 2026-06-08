import paydunya
from django.conf import settings


def _init_paydunya():
    cfg = settings.PAYDUNYA
    paydunya.api_keys = {
        "PAYDUNYA-MASTER-KEY": cfg["MASTER_KEY"],
        "PAYDUNYA-PRIVATE-KEY": cfg["PRIVATE_KEY"],
        "PAYDUNYA-TOKEN": cfg["TOKEN"],
    }
    paydunya.debug = str(cfg["MODE"]).lower() == "test"
    return paydunya.Store(
        name=cfg["STORE_NAME"],
        tagline=cfg["STORE_TAGLINE"],
    )


def get_store():
    if not hasattr(get_store, "_store"):
        get_store._store = _init_paydunya()
    return get_store._store


def get_cfg():
    return settings.PAYDUNYA


def creer_facture(
    montant: int,
    description: str,
    parent_nom: str,
    parent_email: str,
    parent_phone: str,
    **custom_data,
) -> tuple[bool, dict]:
    store = get_store()
    cfg = get_cfg()
    invoice = paydunya.Invoice(store)
    invoice.total_amount = montant
    invoice.description = description
    invoice.customer = {
        "name": parent_nom,
        "phone": parent_phone,
        "email": parent_email,
    }
    invoice.cancel_url = cfg["CANCEL_URL"]
    invoice.return_url = cfg["RETURN_URL"]
    invoice.callback_url = cfg["CALLBACK_URL"]
    if custom_data:
        invoice.add_custom_data(list(custom_data.items()))
    return invoice.create()


def confirmer_paiement(token: str) -> tuple[bool, dict]:
    store = get_store()
    invoice = paydunya.Invoice(store)
    return invoice.confirm(token)
