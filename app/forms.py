from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField


class SQLQEPForm(FlaskForm):
    sql_statement = TextAreaField('SQL Statement')
    qep_plan = TextAreaField('QEP (JSON)')
    submit = SubmitField('VISUALIZE')
