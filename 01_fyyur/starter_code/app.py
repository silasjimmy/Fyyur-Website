#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import ARRAY
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Today's date and time
today = datetime.strptime(datetime.today().strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    genres = db.Column(ARRAY(db.String()))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(200))
    shows = db.relationship('Show', backref='venue', cascade='all, delete, delete-orphan', lazy=True)

    def __repr__(self):
        return self.name

    def past_shows(self):
        return [show for show in self.shows if today > show.start_time]

    def upcoming_shows(self):
        return [show for show in self.shows if today < show.start_time]

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(ARRAY(db.String(10)))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(200))
    shows = db.relationship('Show', backref='artist', cascade='all, delete, delete-orphan', lazy=True)

    def past_shows(self):
        return [show for show in self.shows if today > show.start_time]

    def upcoming_shows(self):
        return [show for show in self.shows if today < show.start_time]

    def __repr__(self):
        return self.name

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))

    def __repr__(self):
        return f"Artist's {self.artist_id} show"

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
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
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city, Venue.state).all()

    venue_details = []

    for city in cities:
        venues = Venue.query.filter(Venue.city==city[0] and Venue.state==city[1]).all()
        venue_details.append({
            "city": city[0],
            "state": city[1],
            "venues": [{
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(venue.upcoming_shows()),
            } for venue in venues]
        })

    return render_template('pages/venues.html', areas=venue_details)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    search_term = request.form.get('search_term').lower()
    venues_search = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()

    results = {
      "count": len(venues_search),
      "data": [{
          "id": venue.id,
          "name": venue.name,
          "num_upcoming_shows": len(venue.upcoming_shows()),
      } for venue in venues_search]
    }

    return render_template('pages/search_venues.html', results=results, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.filter_by(id=venue_id).first()

    past_shows = []
    upcoming_shows = []

    for show in venue.past_shows():
        past_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
        })

    for show in venue.upcoming_shows():
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
      "past_shows_count": len(venue.past_shows()),
      "upcoming_shows_count": len(venue.upcoming_shows())
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    venue_details = request.form

    try:
        venue = Venue(
            name=venue_details.get('name'),
            city=venue_details.get('city'),
            state=venue_details.get('state'),
            address=venue_details.get('address'),
            phone=venue_details.get('phone'),
            image_link=venue_details.get('image_link'),
            facebook_link=venue_details.get('facebook_link'),
            genres=venue_details.getlist('genres'),
            website_link=venue_details.get('website_link'),
            seeking_talent=create_boolean_value(venue_details.get('seeking_talent')),
            seeking_description=venue_details.get('seeking_description')
            )
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        # TODO: on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + venue.name + ' could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    venue = Venue.query.filter_by(id=venue_id).one()
    print(venue)

    try:
        venue = Venue.query.filter_by(id=venue_id).one()
        db.session.delete(venue)
        db.session.commit()
        flash("Venue deleted successfully!")
    except:
        db.session.rollback()
        flash("Venue was not deleted. Something went wrong!")
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database

    artists = Artist.query.order_by('id').all()

    artist_details = []

    for artist in artists:
        artist_details.append({
          "id": artist.id,
          "name": artist.name,
        })

    return render_template('pages/artists.html', artists=artist_details)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term').lower()

    artists_search = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()

    results = {
      "count": len(artists_search),
      "data": [{
          "id": artist.id,
          "name": artist.name,
          "num_upcoming_shows": len(artist.upcoming_shows()),
      } for artist in artists_search]
    }

    return render_template('pages/search_artists.html', results=results, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    artist = Artist.query.filter_by(id=artist_id).first()

    past_shows = []
    upcoming_shows = []

    for show in artist.past_shows():
        past_shows.append({
          "venue_id": show.venue_id,
          "venue_name": show.venue.name,
          "venue_image_link": show.venue.image_link,
          "start_time": str(show.start_time)
        })

    for show in artist.upcoming_shows():
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
      "past_shows_count": len(artist.past_shows()),
      "upcoming_shows_count": len(artist.upcoming_shows())
    }

    return render_template('pages/show_artist.html', artist=artist_details)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist_details = request.form

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
    except:
        db.session.rollback()
        flash('Artist ' + request.form['name'] + ' was not updated. Something went wrong.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()

    # TODO: populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    venue_details = request.form

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
        flash('Venue ' + request.form['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('Venue ' + request.form['name'] + ' was not updated. Something went wrong.')
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
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    artist_details = request.form

    try:
        artist = Artist(
            name=artist_details.get('name'),
            city=artist_details.get('city'),
            state=artist_details.get('state'),
            phone=artist_details.get('phone'),
            genres=artist_details.getlist('genres'),
            image_link=artist_details.get('image_link'),
            facebook_link=artist_details.get('facebook_link'),
            website_link=artist_details.get('website_link'),
            seeking_venue=create_boolean_value(artist_details.get('seeking_venue')),
            seeking_description=artist_details.get('seeking_description')
            )
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

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
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    show_details = request.form

    try:
        show = Show(
            start_time=show_details.get('start_time'),
            artist_id=show_details.get('artist_id'),
            venue_id=show_details.get('venue_id')
        )
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
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
