from flask import Flask, render_template
from flask import request, redirect
import function

app = Flask(__name__)

@app.route('/')
def html():
    return render_template('index.html')

@app.route('/trendPlot', methods = ['POST'])
def trendPlot():
    temp = request.form['trendPlot']
    system = request.form['system']
    new_temp, destination_system = determine_system.determine_system(temp, system)
    return render_template('trendPlot', temp=temp, system=system, new_temp=new_temp, destination_system=destination_system)

@app.route('/transactionFinder', methods = ['POST'])
def transactionFinder():
    temp = request.form['transactionFinder']
    system = request.form['system']
    new_temp, destination_system = determine_system.determine_system(temp, system)
    return render_template('transactionFinder', temp=temp, system=system, new_temp=new_temp, destination_system=destination_system)

if __name__ == "__main__":
    app.run()
