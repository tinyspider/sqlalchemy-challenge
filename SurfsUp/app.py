# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#################################################
# Route for homepage
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of stations: /api/v1.0/stations<br/>"
        f"Temperature for one year:/api/v1.0/tobs<br/>"
        f"Temperature from start date (YYYY-MM-DD):/api/v1.0/<start><br/>"
        f"Temperature from start date to end date (YYYY-MM-DD/YYYY-MM-DD)/api/v1.0/<start>/<end><br/>"
    )
#################################################
# Route for precipitation
# query to retrieve the last 12 months of precipitation data and plot the results. 
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    date_1year_text = start_date()
    precipitation_data = session.query(measurement.date,measurement.prcp)\
        .filter(measurement.date > date_1year_text)\
        .order_by(measurement.date).all()
    session.close()
    return jsonify(dict(precipitation_data))
#################################################
# Route for /api/v1.0/stations
# Returns a json list of stations
#################################################
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    name_stations = session.query(station.station).order_by(station.station).all()
    session.close()
    station_results = list(np.ravel(name_stations))
    return jsonify(station_results)
#################################################
# Route for /api/v1.0/tobs
# Returns a json list of temperature observations (for previous year)
#################################################
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_active_station = 'USC00519281'
    start_str_date = start_date()
    tobs_results = session.query(measurement.date,measurement.tobs)\
                    .filter(measurement.date > start_str_date)\
                    .filter(measurement.station == most_active_station)\
                    .order_by(measurement.date).all()
    session.close()
    return jsonify(dict(tobs_results))
#################################################
# Route for /api/v1.0/<start>
# Enter a date in YYYY-MM-DD format and receive a json list of min. temp., average temp.,
# and max temp. for the date range. (end date = 2017-08-23)
#################################################
@app.route("/api/v1.0/<start>")
def start_date_only(start, end_date='2017-08-23'):
    session = Session(engine)
    result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
                    .filter(measurement.date >= start)\
                    .filter(measurement.date <= end_date).all()
    session.close()
    stats={}
    for min,avg,max in result:
        stats.update({
            'Min':min,
            'Average':avg,
            'Max':max
        })

    # If data exists return it as a json
    if stats['Min']: 
        return jsonify(stats)
    else:
        return jsonify({"error": f"Date {start} not found or not formatted as YYYY-MM-DD."})
#################################################
# Route for /api/v1.0/<start>/<end>
# Enter a start date (YYYY-MM-DD) "/" and an end date (YYYY-MM-DD) to receive a
# json list of min. temp., average temp., and max temp. for the date range. 
# #################################################

@app.route('/api/v1.0/<start>/<end>')
def get_temp_start_end(start, end='2017-08-23'):
    session = Session(engine)
    # Query the db for the min, average, and max temperature oberservations
    # Filter by the start and end date (no end date given = 2017-08-23)
    result = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))\
                        .filter(measurement.date >= start)\
                        .filter(measurement.date <= end).all()
    
    # Close the session
    session.close()
    stats={}
    for min,avg,max in result:
        stats.update({
            'Min':min,
            'Average':avg,
            'Max':max
        })
    if stats['Min']: 
            return jsonify(stats)
    else:
        return jsonify({"error": f"Date {start} not found or not formatted as YYYY-MM-DD."})

#################################################
# funtion to get start date string for most recent 1 year.
#################################################
def start_date():
    session = Session(engine)
    Date_most_recent = (session.query(measurement.date).order_by(measurement.date.desc()).first())[0]
    Date_most_recent = dt.datetime.strptime(Date_most_recent, '%Y-%m-%d').date()
    date_1year = Date_most_recent - dt.timedelta(days = 366)
    date_1year_text = date_1year.strftime('%Y-%m-%d')
    session.close()
    return(date_1year_text)
#################################################
# Run the app
# #################################################
if __name__ == '__main__':
    app.run(debug=True)