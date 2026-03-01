from contact import Contact, sqldb
from sqlalchemy import or_


def get_all_contacts() -> list[Contact]:
    contacts = (
        Contact.query.filter(
            Contact.deletedAt.is_(None),
        )
        .order_by(
            Contact.createdAt.asc(),
        )
        .all()
    )
    return contacts


def get_contacts_by_ids(contact_ids: list[int]) -> list[Contact]:
    if not contact_ids:
        return []
    return (
        Contact.query.filter(
            Contact.id.in_(contact_ids),
            Contact.deletedAt.is_(None),
        )
        .order_by(Contact.createdAt.asc())
        .all()
    )


def get_all_contacts_by_id(contact_id: int) -> list[Contact]:

    return (
        Contact.query.filter(
            or_(
                Contact.id == contact_id,
                Contact.linkedId == contact_id,
            ),
            Contact.deletedAt.is_(None),
        )
        .order_by(Contact.createdAt.asc())
        .all()
    )


def get_linked_contacts_by_ids(contact_ids: list[int]) -> list[Contact]:
    if not contact_ids:
        return []
    return (
        Contact.query.filter(
            Contact.linkedId.in_(contact_ids),
            Contact.deletedAt.is_(None),
        )
        .order_by(Contact.createdAt.asc())
        .all()
    )


def process_identification(email=None, phone_number=None) -> list[Contact]:
    contacts = get_contact_by_email_or_phone(
        email=email,
        phone_number=phone_number,
    )

    # if contacts is empty, create a new contact with new Email/PhoneNumber
    if not contacts:
        create_contact = Contact(
            email=email,
            phoneNumber=phone_number,
            linkPrecedence="primary",
        )
        sqldb.session.add(create_contact)
        sqldb.session.commit()
        contacts.append(create_contact)
        return contacts

    primary_ids = set()
    for contact in contacts:
        if contact.linkPrecedence == "primary":
            primary_ids.add(contact.id)
        elif contact.linkPrecedence == "secondary" and contact.linkedId:
            primary_ids.add(contact.linkedId)

    primary_contacts = get_contacts_by_ids(list(primary_ids))

    if len(primary_contacts) > 1:
        primary_contact = primary_contacts[0]
        new_secondary_contacts = primary_contacts[1:]

        for contact in new_secondary_contacts:
            contact.linkPrecedence = "secondary"
            contact.linkedId = primary_contact.id
            sqldb.session.add(contact)

        new_secondary_ids = [contact.id for contact in new_secondary_contacts]
        new_secondary_linked_contacts = get_linked_contacts_by_ids(
            new_secondary_ids,
        )

        for contact in new_secondary_linked_contacts:
            contact.linkPrecedence = "secondary"
            contact.linkedId = primary_contact.id
            sqldb.session.add(contact)

        sqldb.session.commit()

    contacts = get_all_contacts_by_id(contact_id=primary_contacts[0].id)

    emails = [contact.email for contact in contacts if contact.email]
    phone_numbers = [
        contact.phoneNumber for contact in contacts if contact.phoneNumber
    ]  # type: ignore

    is_input_email_new = bool(email and email not in emails)
    is_input_phone_new = bool(
        phone_number and phone_number not in phone_numbers
    )  # phone_number does not exist in the contacts,

    if is_input_email_new or is_input_phone_new:
        new_contact = Contact(
            email=email,
            phoneNumber=phone_number,
            linkPrecedence="secondary",
            linkedId=primary_contacts[0].id,
        )
        sqldb.session.add(new_contact)
        sqldb.session.commit()
        contacts.append(new_contact)

    return contacts


def get_contact_by_email_or_phone(
    email=None,
    phone_number=None,
) -> list[Contact]:

    query = Contact.query.filter(Contact.deletedAt.is_(None))

    if email and phone_number:
        query = query.filter(
            or_(
                Contact.email == email,
                Contact.phoneNumber == str(phone_number),
            )
        )
    elif email:
        query = query.filter(Contact.email == email)
    elif phone_number:
        query = query.filter(Contact.phoneNumber == str(phone_number))
    else:
        return []

    # sort
    query = query.order_by(Contact.createdAt.asc())

    return query.all()


def build_contacts_response(contacts) -> dict | None:
    if not contacts:
        return None

    primary_contact = contacts[0]

    response = {
        "primaryContactId": primary_contact.id,
        "emails": set(),
        "phoneNumbers": set(),
        "secondaryContactIds": set(),
    }

    for contact in contacts:
        if contact.email:
            response["emails"].add(contact.email)
        if contact.phoneNumber:
            response["phoneNumbers"].add(contact.phoneNumber)
        if contact.id != primary_contact.id:
            response["secondaryContactIds"].add(contact.id)

    # Convert sets to lists for JSON serialization
    response["emails"] = list(response["emails"])
    response["phoneNumbers"] = list(response["phoneNumbers"])
    response["secondaryContactIds"] = list(response["secondaryContactIds"])

    return response


def clear_contacts():
    contacts = Contact.query.all()
    for contact in contacts:
        sqldb.session.delete(contact)
    sqldb.session.commit()
