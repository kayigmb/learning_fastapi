from os import name

from sqlalchemy import select

from database import db, sessionLocal
from models import Roles


def createRoleSeeds():
    roles = [
        {"name": "buyer"},
        {"name": "superadmin"},
        {"name": "admin"},
    ]

    with sessionLocal() as session:
        for role in roles:

            query = session.execute(select(Roles).where(Roles.name == role.get("name")))
            roleFound = query.scalars().all()

            if roleFound:
                continue

            createRole = Roles(name=role["name"])
            session.add(createRole)

        session.commit()
