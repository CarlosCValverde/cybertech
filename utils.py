from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def objects_to_dict(the_object):
    return {
        "id": the_object.id,
        "p_type": the_object.p_type,
        "po_number": the_object.po_number,
        "address": the_object.address,
        "num_chargers": the_object.num_chargers,
        "permit_num": the_object.permit_num,
        "project_status": the_object.project_status,
        "invoice": the_object.invoice,
        "datto": the_object.datto
    }