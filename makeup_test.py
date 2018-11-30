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
    return redirect('/test')

def visualize_local_test():
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

@app.route('/test', methods=['GET'])
def compare_test():
    root = './test_example'
    file_paths = {
                    'old_sql':root+'/old_sql',
                    'new_sql':root+'/new_sql',
                    'old_qep':root+'/old_qep',
                    'new_qep':root+'/new_qep'
                 }
    with open(file_paths['old_sql'], 'r') as file:
        old_sql_str = file.readlines()[0].replace('\n', '')
    with open(file_paths['new_sql'], 'r') as file:
        new_sql_str = file.readlines()[0].replace('\n', '') 
    old_sql = SQLParser(old_sql_str)
    old_sql.scan()
    new_sql = SQLParser(new_sql_str)
    new_sql.scan()
    old_qep = parse_qep(file_paths['old_qep'])
    new_qep = parse_qep(file_paths['new_qep'])
    old_units, old_qep_col, new_units, new_qep_col = new_sql.compare(new_qep, old_qep, old_sql)
    new_js_str = new_qep.convert_to_treant_config(id_to_color=new_qep_col, containerID='newqep')
    old_js_str = old_qep.convert_to_treant_config(id_to_color=old_qep_col, containerID='oldqep')
    js_file_name = "custom-colored-" + get_uid()[:10] + '.js'
    with open(os.path.join("app", "static", js_file_name), "w") as f:
        f.write(new_js_str+old_js_str)
    return render_template('compare_visualize.html', new_sql_units=new_units, old_sql_units=old_units, js_path=js_file_name)
    #pdb.set_trace()


if __name__ == '__main__':
    app.run(debug=True)
    #compare_test()