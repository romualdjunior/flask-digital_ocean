from flask import Flask, request, render_template, redirect, flash, url_for, Response
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
