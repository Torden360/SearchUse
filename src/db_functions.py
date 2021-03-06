from model import (User, Document, Search, Search_Match, Group, Note, connect_to_db, db) 

def load_text(document, name, passcode, doc_owner):
        """ Load the text from the document into database, and create new db object """

        text = document.read()

        document = Document(text=text,
                            name=name,
                            passcode=passcode,
                            doc_owner=doc_owner 
                            )

        db.session.add(document)

        db.session.commit()

        return document


def create_user(username, document_id, is_doc_owner=False):
    """Create new user of document indicated"""

    user = User(username=username,
                document_id=document_id,
                is_doc_owner=is_doc_owner
                )

    db.session.add(user)

    db.session.commit()

    return user


def store_search(search_phrase, document_id):
    """ Store search information into the database """

    search = Search(search_phrase=search_phrase,
                    document_id=document_id)

    db.session.add(search)
    db.session.commit()

    return search.search_id


def create_group(search_id, user_id):
    """ Create new group and store group info """

    group = Group(search_id=search_id,
                  user_id=user_id)

    db.session.add(group)
    db.session.commit()

    return group.group_id


def store_match(search_id, start_offset, end_offset, match_content):
    """ Store saved match info """

    match = Search_Match(search_id=search_id,
                  start_offset=start_offset,
                  end_offset=end_offset,
                  match_content=match_content)

    db.session.add(match)
    db.session.commit()

    return match.match_id


def store_notes(note_content, match_id, group_id):
    """ Store grouped notes per match """

    note = Note(note_content=note_content,
                match_id=match_id,
                group_id=group_id)

    db.session.add(note)
    db.session.commit()


def update_group(group_id, match_id, note_id, note_content):

    pass