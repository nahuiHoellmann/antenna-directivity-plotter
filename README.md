# antenna-directivity-plotter
A simple GUI to plot the directivity of an antenna
This package is divided in two parts:

 1. antools.py which handles the logic in plotting and extracting data point from an excel
 2. A Simple Gui wrapper around antools.py build using PyQt5

For examples on how to use antools.py refer to examples/example.ipynb

## Using the GUI

Setting up the environment:

    cd <path>/antools-directivity-plotter
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
   
Running the app without QtCreator:
   

    python main.py

Runnig the app in debug mode loads a mock DataFrame as 
data in order to preview app without waiting for a file to load

    python main.py -d

Optionaly you can open the app using QtCreator
