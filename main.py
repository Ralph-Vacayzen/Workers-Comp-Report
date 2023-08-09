import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(
    page_title='Workers Comp Report',
    page_icon='📄'
)

st.caption('VACAYZEN')
st.title('Workers Comp Report')
st.info('A tool used to produce workers comp summations.')

st.header('Required reports')
st.write('Payroll Register Data Export')
with st.expander('How to pull report'):
    st.write('[Paylocity | Reporting](https://app.paylocity.com/reporting/reports)')
    st.video('https://youtu.be/1AC-LRTg8ck')

file = st.file_uploader('Payroll Register Data Export.csv','csv')
if file is not None: df = pd.read_csv(file, index_col=False)

if (file is not None):
    st.divider()

    st.header('Defined Fields')

    amounts  = []
    overtime = ''
    tips     = ''

    for column in df.columns:
        if 'Amount' in column: amounts.append(column)
    
    for column in amounts:
        if 'OT' in column:   overtime = column
        if 'TIPS' in column: tips     = column
    
    overtime = amounts.index(overtime)
    tips     = amounts.index(tips)

    fields_gross   = st.multiselect('Applicable for Gross Pay',amounts,amounts)
    st.info('Paylocity does not included 401K in thier "gross pay" that appears on pay stubs.')
    field_overtime = st.selectbox('Applicable for Overtime',    amounts,overtime)
    field_tips     = st.selectbox('Applicable for Tips',        amounts,tips)

    df['gross_pay'] = df.loc[:,fields_gross].sum(axis=1)
    df['overtime']  = df[field_overtime]
    df['tips']      = df[field_tips]

    df       = df[['Employee','Location','gross_pay','overtime','tips']]
    employee = df.groupby(['Employee','Location']).sum().sort_values(by=['Location','Employee'])
    employee = employee.reset_index()
    employee.columns = ['employee','classification','gross_pay','overtime','tips']
    category = employee.groupby('classification').count().reset_index().drop(['gross_pay','overtime','tips'],axis=1)
    category = pd.merge(category, employee.groupby('classification').sum(numeric_only=True).reset_index(), on='classification')
    category = category[['employee','classification','gross_pay','overtime','tips']]
    category = category.rename(columns={'employee':'employees'})

    st.divider()

    st.header('Metrics')

    with st.container():
        left, middle, right = st.columns(3)
        left.metric('Employees', np.sum(category.employees))
        middle.metric('Classifications', len(category.classification))
    
    with st.container():
        left, middle, right = st.columns(3)
        left.metric('Gross Pay',  round(np.sum(category.gross_pay),2))
        middle.metric('Overtime', round(np.sum(category.overtime),2))
        right.metric('Tips',      round(np.sum(category.tips),2))
    
    st.divider()

    st.subheader('Employee Summary')
    st.dataframe(employee,hide_index=True,use_container_width=True)
    st.download_button('Download Employee Summary',employee.to_csv(index=False),'employee_summary.csv',use_container_width=True)
    st.subheader('Category Summary')
    st.dataframe(category,hide_index=True,use_container_width=True)
    st.download_button('Download Category Summary',category.to_csv(index=False),'category_summary.csv',use_container_width=True)