from sqlalchemy.orm import Session
from datetime import datetime
from models import Contact


# commit: add reconciliation service logic
def reconcile(db: Session, email: str | None, phone: str | None) -> dict:
    # fetching all contacts matching either email or phone
    matched = []

    if email:
        matched += db.query(Contact).filter(
            Contact.email == email, Contact.deletedAt == None
        ).all()

    if phone:
        matched += db.query(Contact).filter(
            Contact.phoneNumber == phone, Contact.deletedAt == None
        ).all()

    # deduplicate by id
    seen = {}
    for c in matched:
        seen[c.id] = c
    matched = list(seen.values())

    if not matched:
        new_contact = Contact(
            email=email,
            phoneNumber=phone,
            linkPrecedence="primary",
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)

        return build_response(db, new_contact)

    # gather all primaries from the matched set
    # some matched contacts may themselves be secondary — resolve their primary
    primary_ids = set()
    for c in matched:
        if c.linkPrecedence == "primary":
            primary_ids.add(c.id)
        else:
            primary_ids.add(c.linkedId)

    primaries = db.query(Contact).filter(Contact.id.in_(primary_ids)).all()

    if len(primaries) > 1:
        # oldest by createdAt wins
        primaries.sort(key=lambda c: c.createdAt)
        true_primary = primaries[0]
        to_demote = primaries[1:]

        for p in to_demote:
            p.linkPrecedence = "secondary"
            p.linkedId = true_primary.id
            p.updatedAt = datetime.utcnow()

            # also reassign all their secondaries to the true primary
            db.query(Contact).filter(
                Contact.linkedId == p.id
            ).update(
                {"linkedId": true_primary.id, "updatedAt": datetime.utcnow()},
                synchronize_session=False,
            )

        db.commit()
    else:
        true_primary = primaries[0]

    # commit: create new secondary if new info was introduced
    all_contacts = db.query(Contact).filter(
        (Contact.id == true_primary.id) | (Contact.linkedId == true_primary.id),
        Contact.deletedAt == None,
    ).all()

    existing_emails = {c.email for c in all_contacts if c.email}
    existing_phones = {c.phoneNumber for c in all_contacts if c.phoneNumber}

    new_info = (email and email not in existing_emails) or \
               (phone and phone not in existing_phones)

    if new_info:
        secondary = Contact(
            email=email,
            phoneNumber=phone,
            linkedId=true_primary.id,
            linkPrecedence="secondary",
        )
        db.add(secondary)
        db.commit()

    return build_response(db, true_primary)


def build_response(db: Session, primary: Contact) -> dict:
    all_contacts = db.query(Contact).filter(
        (Contact.id == primary.id) | (Contact.linkedId == primary.id),
        Contact.deletedAt == None,
    ).order_by(Contact.createdAt).all()

    emails = []
    phones = []
    secondary_ids = []

    # primary always goes first in emails/phones if present
    if primary.email and primary.email not in emails:
        emails.append(primary.email)
    if primary.phoneNumber and primary.phoneNumber not in phones:
        phones.append(primary.phoneNumber)

    for c in all_contacts:
        if c.id == primary.id:
            continue
        secondary_ids.append(c.id)
        if c.email and c.email not in emails:
            emails.append(c.email)
        if c.phoneNumber and c.phoneNumber not in phones:
            phones.append(c.phoneNumber)

    return {
        "primaryContatctId": primary.id,
        "emails": emails,
        "phoneNumbers": phones,
        "secondaryContactIds": secondary_ids,
    }
