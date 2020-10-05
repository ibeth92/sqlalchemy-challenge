# Python SQL toolkit and Object Relational Mapper
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func

# Import Flask 
from flask import Flask, jsonify

# Setup Database
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# Automap base
Base = automap_base()

# Reflect an existing database into a new model
Base.prepare(engine, reflect= True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

# Setup Flask
# Create an app, pass to __name__
app = Flask(__name__)

# Flask Routes 
@app.route("/")
def welcome():
    return(
        f"Hawaii Climate API<br/>"
        f"Avaialble Routes:<br>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
# Set up Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
# Create our session (link) from Python to the DB
    session = Session(engine)

# Query Measurement date and Precipitation
    results =   session.query(Measurement.date, Measurement.prcp).\
                order_by(Measurement.date).all()

# Convert to list of dictionaries to jsonify
    precip_date_list = []

    for date, prcp in results:
        new_dict = {}
        new_dict[date] = precip
        precip_date_list.append(new_dict)

    session.close()

    return jsonify(precip_date_list)

# Set up Stations
@app.route("/api/v1.0/stations")
def stations():

# Create our session (link) from Python to the DB
    session = Session(engine)

    stations = {}

# Query all stations
    results = session.query(Station.station, Station.name).all()
    for sta, name in results:
        stations[sta] = name

    session.close()
 
    return jsonify(stations)

# Set up Tobs
@app.route("/api/v1.0/tobs")
def tobs():

# Create our session (link) from Python to the DB
    session = Session(engine)

# Query all Temperatures for the most active station ID
    temp_active = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == "USC00519281").filter(Measurement.date).all()
    session.close()
    temp_list = list(np.ravel(temp_active))
    return jsonify(temp_list)

# Set up start and end
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<ends>")
def tempdata(start, end):
    startdate = start
    endate = end
    session = Session(engine)

    if type(endate) is not datetime.date:
        endate = "2020-08-31"
        select = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]
        stats = session.query(*select).fliter(Measurement.date >=startdate).all()
        results = list(np.ravel(stats))
        return jsonify(results)

    if type(startdate) is not datetime.date:
        startdate = "1992-08-31"
        select = [func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)]
        stats = session.query(*select).filter(Measurement.date >=startdate).filter(Measurement.date >=endate).all()
        results = list(np.ravel(stats))
        session.close()
        return jsonify(results)

if __name__ == '__main__':
        app.run(debug=True)
        