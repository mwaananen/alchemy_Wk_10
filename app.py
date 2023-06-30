# Import the dependencies.

import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
base = automap_base()

# reflect the tables
base.prepare(autoload_with=engine)

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome(): 
    #All API routes listed
    """All API Routes"""
    
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    #Query results from your precipitation analysis
    one_year = dt.date(2017,8,23) -dt.timedelta(days=365)

    twelve_mo = session.query(measurement.date, measurement.prcp).filter(measurement.date > one_year).order_by(measurement.date).all()
    
    session.close()
    
    #Convert the query to a dictionary
    precipitation_results =[]
    for date, prcp in twelve_mo:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precipitation_results.append(precipitation_dict)
    
    #Return JSON representation
    return jsonify(precipitation_results)

@app.route("/api/v1.0/stations")
def stations():
    #Return a JSON list of stations
    
    station_list = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).all()
    
    session.close()
    
    all_stations = list(np.ravel(station_list))
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temps():
    #Date and temperature observations of the most-active station for the previous year
    one_year = dt.date(2017,8,23) -dt.timedelta(days=365)

    most_active = [func.min(measurement.tobs),
                  func.max(measurement.tobs),
                  func.avg(measurement.tobs), 
                  (measurement.date)]
    
    active_year_temps = session.query(*most_active).filter(measurement.station == 'USC00519281').\
    filter(measurement.date > one_year).all()
    
    session.close()
    
    active_all = list(np.ravel(active_year_temps))
    
    return jsonify(active_all)

@app.route("/api/v1.0/<start>")
def start_one(start):
 # go back one year from start date and go to end of data for Min/Avg/Max temp
    
    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end =  dt.date(2017, 8, 23)
   
    trip_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    trip = list(np.ravel(trip_data))
    
    return jsonify(trip)

@app.route("/api/v1.0/<start>/<end>")
def start_two(start,end):
  # go back one year from start/end date and get Min/Avg/Max temp

    start_date= dt.datetime.strptime(start, '%Y-%m-%d')
    end_date= dt.datetime.strptime(end,'%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start = start_date-last_year
    end = end_date-last_year

    trip_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    
    trip = list(np.ravel(trip_data))

    return jsonify(trip)

if __name__ == '__main__':
    app.run(debug=True)

    