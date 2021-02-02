from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import matplotlib.colors as colors      # create visaulizations 
import matplotlib.image as mpimg        # create visaulizations 
import matplotlib.pyplot as plt         # create visaulizations
from termcolor import colored           # prints colored text 
from zipfile import ZipFile             # zip file manipulation 
from os.path import join                # data access in file manager
from glob import iglob                  # data access in file manager 
import pandas as pd                     # data analysis and manipulation
import numpy as np                      # scientific computing
import subprocess                       # external calls to system
import snappy                           # SNAP python interface
from snappy import *
import os
# change module setting 
pd.options.display.max_colwidth = 80

app = Flask(__name__)
CORS(app)

@app.route('/take_photo/<word>')
def hello(word):
    from sentinelsat.sentinel import SentinelAPI, read_geojson, geojson_to_wkt
    from datetime import date
    
    # connect to the API
    api = SentinelAPI('swinburncarlos', 'CsVd1324#', 'https://scihub.copernicus.eu/dhus')
    
    # download single scene by known product id
    footprint = geojson_to_wkt(read_geojson('static/data.geojson'))
    products = api.query(footprint,
                         producttype='SLC',
                         orbitdirection='ASCENDING')
    print('lelel')
    
    footprint = geojson_to_wkt(read_geojson('static/data.geojson'))
    data = 'done proceing'
    products = api.query(footprint, date=('20200201', date(2020, 2, 1)), platformname='Sentinel-2')
    #api.download_all(products)
    products_df = api.to_dataframe(products)

    # sort and limit to first 5 sorted products
    products_df_sorted = products_df.sort_values(['cloudcoverpercentage', 'ingestiondate'], ascending=[True, True])
    products_df_sorted = products_df_sorted.head(5)

    # download sorted and reduced products
    api.download_all(products_df_sorted.index)
    print(products_df)
    print(type(products_df))
    return render_template('base.html',data=data)

    # convert to Pandas DataFrame
    print (products_df)

def ApplyOrbitFile(products):
    parameters = snappy.HashMap()
    parameters.put('Apply-Orbit-File',True)
    apply_orbit = snappy.GPF.crateProduct('Apply-Orbit-File', parameters,  products)
    print(colored('Orbit updates succesfully','green'))
    return apply_orbit
    


@app.route('/',methods=['GET', 'POST'])
@cross_origin()
def home():
    if request.method == 'POST':
        file = request.files['exc']
        ext = (file.filename.split('.'))[1]
        if ext == 'geojson':
            file_path = os.path.join("static","data.geojson")
            file.save(file_path)
            word = 'Submited!'
        else:
            return render_template('base.html',data='404 bad ext')
        return render_template('base.html',data=word)
    else:
        word = 'homepage'
        return render_template('base.html',data=word)
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)