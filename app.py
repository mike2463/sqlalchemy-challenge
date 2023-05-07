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
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
stations = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"

    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    preceip_scores = session.query(measurement.date, measurement.prcp).\
    filter(measurement.date >= year_ago).\
    order_by(measurement.date).all()
    session.close()
    precip = {date: prcp for date, prcp in preceip_scores}
    return jsonify(precip)

@app.route('/api/v1.0/stations')
def stations_func():
    total_stations = session.query(stations.station, stations.name).all()
    stations_dict = {station: name for station, name in total_stations}
    session.close()
    return jsonify(stations_dict)

@app.route('/api/v1.0/tobs')
def tabs():
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   
    active_stations = session.query(measurement.station, func.count(measurement.station)).\
    group_by(measurement.station).\
    order_by(func.count(measurement.station).desc()).all()
    
    most_active = active_stations[0][0]
    
    sel = [measurement.tobs]
    
    most_active_temps = session.query(*sel).\
    filter(measurement.station == most_active).all()

    session.close()
    
    all_tops = list(np.ravel(most_active_temps))
    
    return jsonify(all_tops)

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def start_end(start = None, end = None):
    sel = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]
    
    if not end: 
        start = dt.datetime.strptime(start, '%Y%m%d')
    
        
        
        most_active_temps = session.query(*sel).\
            filter(measurement.station >= start).all()
        session.close()
    
        temps = list(np.ravel(most_active_temps))
        return jsonify(temps)
    
    start = dt.datetime.strptime(start, '%Y%m%d')
    
    end = dt.datetime.strptime(end, '%Y%m%d')
    
    most_active_temps = session.query(*sel).\
        filter(measurement.station >= start).\
        filter(measurement.station >= end).all()
    session.close()
    
    temps = list(np.ravel(most_active_temps))
    return jsonify(temps)








if __name__ == '__main__':
    app.run(debug=True)
