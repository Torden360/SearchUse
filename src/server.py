from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, jsonify, make_response, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import (Document, Search, Search_Match, connect_to_db, db) 
# will add Group, Group_Match, and Comment after MVP

from werkzeug.utils import secure_filename

from sqlalchemy import func

from db_functions import load_text, store_search, create_group, store_match, store_notes

from search import search


ALLOWED_EXTENSIONS = {'txt'}
# not sure that I will use this/if I need it when I am forcing the accept params
# on the html itself. Which is better to do that with?/More secure

app = Flask(__name__)

app.secret_key = "ABC"


@app.route('/')
def display_homepage():
    """ Displays homepage """

    file = Document.query.get(3)
    # testing this for now -- will remove once satisfied with results of db queries

    searches = file.searches
        # matches = user_search.query.filter(user_search.search_id == search_id)

    return render_template('homepage.html', file=file)
    # Took these out of route for now
    # text = bytes.decode(file.text)
    # return render_template('homepage.html', file=file, text=text)


@app.route('/user_groups')
def display_groups():
    """ Displays user's groups """

    file = Document.query.get(3)
    # testing this for now -- will remove once satisfied with results of db queries

    searches = file.searches

    groups = []

    for user_search in searches:
        group = user_search.groups
        if group:
            search_phrase = user_search.search_phrase
            matches = user_search.search_matches
            group_dict = {}
            groups.append((search_phrase, group_dict))
            for match in matches:
                match_content = match.match_content
                group_dict['match_content'] = match_content
                notes = match.notes
                if notes:
                    note = notes[0].note_content
                    group_dict['note'] = note

    groups = jsonify(groups)

    return groups


@app.route('/upload_file')
def upload_document():
    """ Allows user to upload a document """

    return render_template("upload_file.html")


@app.route('/file_view', methods=['POST'])
def display_document():
    """ Displays the document of user's choice """

    file = request.files['file']
    # retrieves the uploaded file

    filename = request.form.get('filename')
    # gets the filename that was entered by the user

    file = load_text(file, filename)
    # call load_text FN with the file and filename

    text = bytes.decode(file.text)
    # decodes byte string

    return render_template("file_view.html", file=file, text=text)



# developping this in the most basic/redundant way for now

@app.route('/search_view')
def search_document():
    """ Gets and stores user's input search on the given document """

    search_phrase = request.args.get('search_phrase')
    # gets the search phrase that was entered by the user

    document_id = request.args.get('doc_id')

    search_id = store_search(search_phrase, document_id)

    file = Document.query.get(document_id)
    text = bytes.decode(file.text)

    matches = search(search_phrase, text)

    return render_template("file_view.html", file=file, text=text, 
        search_phrase=search_phrase, search_id=search_id, matches=matches)


# This route is incomplete
@app.route('/save_grouped_matches', methods=['POST'])
def save_matches():
    """ Saves the matches and notes in a group """

    req = request.get_json()

    print('This is json from front end!!', req)

    search_id = req['search_id']
    group_id = create_group(search_id)

    for match in req['matches']:

        start_offset = match['start_offset']
        end_offset = match['end_offset']
        match_content = match['match_content']

        match_id = store_match(search_id, start_offset, end_offset, match_content)

        if match['notes']:
            note_content = match['notes']
            store_notes(note_content, match_id, group_id)

    # this flash message is currently not working, just mocked out for now
    flash('Your search matches and notes have been saved')
    

    res = make_response(jsonify(req), 200)

    return res



if __name__ == "__main__":

    app.debug = True
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')