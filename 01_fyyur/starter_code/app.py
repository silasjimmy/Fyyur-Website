#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from datetime import datetime
import dateutil.parser
import babel
from flask import (
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for
)
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    '''
    Transforms the date to the desired format.

    Parameters:
        value (obj): Date object.
        format (str): The format to transform to.
    Returns:
        The date inn the desired format.
    '''

    date = dateutil.parser.parse(value)

    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"

    return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Helper functions.
#----------------------------------------------------------------------------#

def create_boolean_value(answer):
    '''
    Creates a boolean value.

    Parameters:
        answer (str): y for yes and n for no.
    Returns:
        bool (bool): True if y, False otherwise.
    '''

    bool_value = True if answer == 'y' else False
    return bool_value

def create_genre_list(genres_str):
    '''
    Creates a list of genres.
    Parameters:
        genres_str (str): string of genres, braces and commas.
    Returns:
        genres (list): list of genres.
    '''

    genres = ''.join(genres_str)
    genres = genres.strip('{}')
    genres = genres.split(',')

    return genres

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()

    venue_details = []

    for city in cities:
        venues = Venue.query.filter(Venue.city==city[0] and Venue.state==city[1]).all()
        upcoming_shows_query = db.session.query(Show).join(Venue).filter(Venue.city==city[0] and Venue.state==city[1]).all()
        venue_details.append({
            "city": city[0],
            "state": city[1],
            "venues": [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(upcoming_shows_query),
            } for venue in venues]
        })

    return render_template('pages/venues.html', areas=venue_details)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term').lower()
    venues_search = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

    results = {
      "count": len(venues_search),
      "data": [{
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(db.session.query(Show).join(Venue). \
          filter(Venue.id==venue.id).filter(Show.start_time > datetime.now()).all()),
      } for venue in venues_search]
    }

    return render_template('pages/search_venues.html', results=results, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).first()

    past_shows_query = db.session.query(Show).join(Venue).filter(Venue.id == venue_id).filter(Show.start_time < datetime.now()).all()
    upcoming_shows_query = db.session.query(Show).join(Venue).filter(Venue.id == venue_id).filter(Show.start_time > datetime.now()).all()

    past_shows = []
    upcoming_shows = []

    for show in past_shows_query:
        past_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
        })

    for show in upcoming_shows_query:
        upcoming_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
        })

    venue_details = {
      "id": venue.id,
      "name": venue.name,
      "genres": create_genre_list(venue.genres),
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows_query),
      "upcoming_shows_count": len(upcoming_shows_query)
    }

    return render_template('pages/show_venue.html', venue=venue_details)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form = VenueForm(request.form)

    try:
        venue = Venue()
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully listed!')
    except Exception:
        flash('An error occurred. Venue ' + request.form.get('name') + ' could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.filter_by(id=venue_id).one()

    try:
        venue = Venue.query.filter_by(id=venue_id).one()
        db.session.delete(venue)
        db.session.commit()
        flash("Venue deleted successfully!")
    except Exception:
        db.session.rollback()
        flash("Venue was not deleted. Something went wrong!")
    finally:
        db.session.close()

    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    artists = Artist.query.all()
    print(artists)

    artist_details = []

    for artist in artists:
        artist_details.append({
          "id": artist.id,
          "name": artist.name,
        })

    return render_template('pages/artists.html', artists=artist_details)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    search_term = request.form.get('search_term').lower()

    artists_search = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

    results = {
      "count": len(artists_search),
      "data": [{
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": len(db.session.query(Show).join(Artist). \
          filter(Artist.id==artist.id).filter(Show.start_time > datetime.now()).all()),
      } for artist in artists_search]
    }

    return render_template('pages/search_artists.html', results=results, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.filter_by(id=artist_id).first()

    past_shows_query = db.session.query(Show).join(Artist).filter(Artist.id == artist_id).filter(Show.start_time < datetime.now()).all()
    upcoming_shows_query = db.session.query(Show).join(Artist).filter(Artist.id == artist_id).filter(Show.start_time > datetime.now()).all()

    past_shows = []
    upcoming_shows = []

    for show in past_shows_query:
        past_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
        })

    for show in upcoming_shows_query:
        upcoming_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
        })

    artist_details = {
      "id": artist.id,
      "name": artist.name,
      "genres": create_genre_list(artist.genres),
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows_query),
      "upcoming_shows_count": len(upcoming_shows_query)
    }

    return render_template('pages/show_artist.html', artist=artist_details)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()

    artist = Artist.query.get(artist_id)

    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist_details = request.form

    form =  ArtistForm(artist_details)

    try:
        artist = Artist.query.get(artist_id)
        artist.name = artist_details.get('name')
        artist.city = artist_details.get('city')
        artist.state = artist_details.get('state')
        artist.phone = artist_details.get('phone')
        artist.genres = artist_details.getlist('genres')
        artist.image_link = artist_details.get('image_link')
        artist.facebook_link = artist_details.get('facebook_link')
        artist.website_link = artist_details.get('website_link')
        artist.seeking_venue = create_boolean_value(artist_details.get('seeking_venue'))
        artist.seeking_description = artist_details.get('seeking_description')
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully updated!')
    except Exception:
        db.session.rollback()
        flash('Artist ' + request.form['name'] + ' was not updated. Something went wrong.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    venue = Venue.query.get(venue_id)

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue_details = request.form

    form = VenueForm(venue_details)

    try:
        venue = Venue.query.get(venue_id)
        venue.name = venue_details.get("name")
        venue.city = venue_details.get("city")
        venue.state = venue_details.get("state")
        venue.address = venue_details.get("address")
        venue.phone = venue_details.get("phone")
        venue.genres = venue_details.getlist("genres")
        venue.facebook_link = venue_details.get("facebook_link")
        venue.image_link = venue_details.get("image_link")
        venue.website_link = venue_details.get("website_link")
        venue.seeking_talent = create_boolean_value(venue_details.get("seeking_talent"))
        venue.seeking_description = venue_details.get("seeking_description")
        db.session.commit()
        flash('Venue ' + venue_details.get('name') + ' was successfully updated!')
    except Exception:
        db.session.rollback()
        flash('Venue ' + venue_details.get('name') + ' was not updated. Something went wrong.')
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form = ArtistForm(request.form)

    try:
        artist = Artist()
        form.populate_obj(artist)
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + artist.name + ' was successfully listed!')
    except Exception:
        flash('An error occurred. Artist ' + request.form.get('name') + ' could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    show_details = []
    shows = Show.query.order_by('venue_id').all()

    for show in shows:
        show_details.append({
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "artist_id": show.artist.id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time)
        })

    return render_template('pages/shows.html', shows=show_details)

@app.route('/shows/create')
def create_shows():
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    form = ShowForm(request.form)

    try:
        show = Show()
        form.populate_obj(show)
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except Exception:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('errors/500.html'), 401

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
