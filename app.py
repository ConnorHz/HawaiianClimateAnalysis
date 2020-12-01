from flask import Flask, jsonify, render_template
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import *

import numpy as np
import pandas as pd

import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
meta = MetaData()

station = Table('station', meta, autoload_with=engine, extend_existing=True)
measurement = Table('measurement', meta, Column('date', Date), autoload_with=engine, extend_existing=True)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

@app.route("/", methods=['GET'])
def home():
    return render_template("index.html")

@app.route("/api/v1.0/precipitation", methods=['GET'])
def precipitation():
    session = Session(engine)

    results = session.query(measurement.c.date, measurement.c.prcp).all()

    session.close()

    precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        precipitation.append(precipitation_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations", methods=['GET'])
def stations():
    session = Session(engine)

    results = session.query(station).all()

    session.close()

    stations = []
    for station_id, station_guid, name, latitude, longitude, elevation in results:
        station_dict = {}
        station_dict["id"] = station_id
        station_dict["station"] = station_guid
        station_dict["name"] = name
        station_dict["latitude"] = latitude
        station_dict["longitude"] = longitude
        station_dict["elevation"] = elevation
        stations.append(station_dict)

    return jsonify(stations)

@app.route("/api/v1.0/tobs", methods=['GET'])
def tobs():
    session = Session(engine)

    last_date = session.query(func.max(measurement.c.date)).first()[0]
    year_ago = last_date - dt.timedelta(days=365)

    most_active_station = session.query(station.c.station, func.count(measurement.c.station)).\
    filter(station.c.station == measurement.c.station).\
    filter(measurement.c.date >= year_ago).\
    group_by(station.c.station).\
    order_by(func.count(measurement.c.station).desc()).\
    first()[0]

    results = session.query(measurement.c.date, measurement.c.prcp).\
    filter(measurement.c.station == most_active_station).\
    filter(measurement.c.date >= year_ago).\
    all()

    session.close()

    station_precipitation = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        station_precipitation.append(precipitation_dict)

    return jsonify(station_precipitation)

@app.route("/api/v1.0/<start_date>", methods=['GET'])
def temp_start(start_date):
    session = Session(engine)

    temp_agg = session.query(func.min(measurement.c.tobs), func.avg(measurement.c.tobs), func.max(measurement.c.tobs)).\
        filter(measurement.c.date >= start_date).all()[0]

    session.close()

    temp_dict = {}
    temp_dict["TMIN"] = temp_agg[0]
    temp_dict["TAVG"] = temp_agg[1]
    temp_dict["TMAX"] = temp_agg[2]

    return jsonify(temp_dict)

@app.route("/api/v1.0/<start_date>/<end_date>", methods=['GET'])
def temp_start_end(start_date, end_date):
    session = Session(engine)

    temp_agg = session.query(func.min(measurement.c.tobs), func.avg(measurement.c.tobs), func.max(measurement.c.tobs)).\
        filter(measurement.c.date >= start_date).filter(measurement.c.date <= end_date).all()[0]

    session.close()

    temp_dict = {}
    temp_dict["TMIN"] = temp_agg[0]
    temp_dict["TAVG"] = temp_agg[1]
    temp_dict["TMAX"] = temp_agg[2]

    return jsonify(temp_dict)


if __name__ == "__main__":
    app.run(debug=True)
