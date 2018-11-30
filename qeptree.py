import json
import os
from flask import Flask
from flask import request, render_template, make_response, redirect, flash, url_for, jsonify
from app.sql_parser import SQLParser
from qep_parser import parse_qep, parse_qep_str
from app import create_app
from app.utils import get_uid
from app.forms import *
import pdb

app = create_app()


@app.route('/')
def index():
    return redirect('/visualize')


@app.route('/visualize', methods=['GET', 'POST'])
def visualize_view():
    form = SQLQEPForm()
    if form.validate_on_submit():
        sql_str = form.sql_statement.data
        qep_str = form.qep_plan.data
        p = SQLParser(sql_str)
        p.scan()
        qep_root = parse_qep_str(qep_str)
        sql_units, sql_to_qep, qep_to_sql, qep_to_col = p.reconstruct(qep_root)
        js_str = qep_root.convert_to_treant_config(id_to_color=qep_to_col)
        js_file_name = "custom-colored-" + get_uid()[:10] + '.js'
        with open(os.path.join("app", "static", js_file_name), "w") as f:
            f.write(js_str)
        return render_template('sql_qep_visualize.html', sql_units=sql_units, js_path=js_file_name)
    return render_template('index.html', form=form)




@app.route('/visualize-local', methods=['GET'])
def visualize_local_view():
    with open('test_sql.json') as f:
        sql_data = json.load(f)
    sql_str = sql_data.get('sql')
    p = SQLParser(sql_str)
    p.scan()
    qep_root = parse_qep("test_qep.json")
    sql_units, sql_to_qep, qep_to_sql, qep_to_col = p.reconstruct(qep_root)
    js_str = qep_root.convert_to_treant_config(id_to_color=qep_to_col)
    js_file_name = "custom-colored-" + get_uid()[:10] + '.js'
    with open(os.path.join("app", "static", js_file_name), "w") as f:
        f.write(js_str)
    return render_template('sql_qep_visualize.html', sql_units=sql_units, js_path=js_file_name)


if __name__ == '__main__':
    app.run(debug=True)
