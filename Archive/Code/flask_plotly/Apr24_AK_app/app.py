from flask import Flask, config, render_template, request
from flask_pymongo import PyMongo
import pandas as pd
import json
import plotly
import plotly.express as px
import plotly.figure_factory as ff
import numpy as np

# SETUP --------------------------------------------------------------

app = Flask(__name__, template_folder = 'templates')

app.config["MONGO_DBNAME"] = "TaxRecords"
app.config["MONGO_URI"] = "mongodb+srv://DS6013_Students_Ami:DS6013_Students_AK@countyrecords.4cdfgz2.mongodb.net/TaxRecords?retryWrites=true&w=majority"

mongo = PyMongo(app)
columns = list(mongo.db["Tax_Record_1867"].find_one({}, {'_id':False}))

# HOMEPAGE --------------------------------------------------------------

@app.route('/callback', methods=['POST', 'GET'])
def cb():
    return gm(request.args.get('data'))
   
@app.route('/')
def index():
    return render_template('main_page.html',  graphJSON=gm())

def gm(EventLocJurisdictionCounty='Fluvanna'):
#def gm():
    #df = pd.read_csv('Tax_1867_Cleaned.csv')

    # find is a pymongo function to select the entire collection; list makes it iterable; then make a pandas df
    # df = pd.DataFrame(list(mongo.db["Tax_Record_1867"].find()))
    df = pd.DataFrame(list(mongo.db['Tax_Record_1867']\
            .find({}, 
                  {"PersonTaxLeviedLand":1, 
                   "PersonTaxStateAll": 1,
                   "PersonEventRole":1,
                   'EventLocJurisdictionCounty':1,
                   'PersonsTaxedCountWMalesover21':1, 
                   'PersonsTaxedCountNMalesover21':1,
                   'PersonRoleLocSurnameEmployer':1,
                   'PersonSurname':1,
                   'SourceLocCreatedCounty':1,
                   '_id':0})))

    # add condition for whether employer and person have same last name
    conditions = [
        (df['PersonRoleLocSurnameEmployer']==df['PersonSurname']),
        (df['PersonRoleLocSurnameEmployer']!=df['PersonSurname'])
        ]

    values = ['Confirmed', 'Unconfirmed']

    df['FormerlyEnslaved'] = np.select(conditions, values)

    # if trying to use callback function:
    #fig1 = px.histogram(df[df['EventLocJurisdictionCounty']==EventLocJurisdictionCounty], x="PersonEventRole", y="PersonTaxStateAll",
    
    # if not:
    fig1 = px.histogram(df, x="PersonEventRole", y="PersonTaxStateAll",
             color="SourceLocCreatedCounty", 
             color_discrete_sequence=px.colors.qualitative.Antique,
             barmode='group',
             width=800, height=500)
    
    fig1.update_layout(
        title={'text':"Total Tax Amount by Role and County",
               'x':0.5,
               'xanchor': 'center'},
        xaxis_title="Sum of State Tax Total Amount",
        yaxis_title="Person Role",
        legend_title="County",
        font=dict(
            family="Segoe UI",
            size=16,
        )
    )
    
    fig2 = px.histogram(df, x='EventLocJurisdictionCounty', y='PersonsTaxedCountNMalesover21',
             color="PersonEventRole", 
             color_discrete_sequence=px.colors.qualitative.Antique,
             barmode='group',
             width=800, height=500)
    
    fig2.update_layout(
        title={'text': "Count of Black Males by Role and County",
               'x':0.5,
               'xanchor': 'center'},
        xaxis_title="County",
        yaxis_title="Sum of Black Males over 21",
        legend_title="Person Role",
        font=dict(
            family="Segoe UI",
            size=16)
    )
    
    fig3 = px.histogram(df, x='EventLocJurisdictionCounty', y='PersonsTaxedCountWMalesover21',
             color="PersonEventRole", 
             color_discrete_sequence=px.colors.qualitative.Antique,
             barmode='group',
             width=800, height=500)
    
    fig3.update_layout(
        title={'text':"Count of White Males by Role and County",
               'x':0.5,
               'xanchor': 'center'},
        xaxis_title="County",
        yaxis_title="Sum of White Males over 21",
        legend_title="Person Role",
        font=dict(
            family="Segoe UI",
            size=16)
    )
    
    fig4 = px.histogram(df, x="PersonEventRole", y="PersonTaxStateAll",
             color="FormerlyEnslaved",
             color_discrete_sequence=px.colors.qualitative.Antique,
             barmode="group",
             width=800, height=500)
    
    fig4.update_layout(
        title={'text':"Total Tax Amount by Role and Former Enslavement Status",
               'x':0.5,
               'xanchor': 'center'},
        xaxis_title="Role",
        yaxis_title="Sum of State Tax Total Amount",
        legend_title="Former Enslavement Status",
        font=dict(
            family="Segoe UI",
            size=16)
    )

    fig5 = px.histogram(df, x="PersonEventRole", y="PersonTaxStateAll",
            color="FormerlyEnslaved",
            color_discrete_sequence=px.colors.qualitative.Antique,
            barmode="group", histfunc='avg',
            width=800, height=500)
    
    fig5.update_layout(
        title={'text':"Average Total Tax Amount by Role and Former Enslavement Status",
               'x':0.5,
               'xanchor': 'center'},
        xaxis_title="Role",
        yaxis_title="Average of State Tax Total Amount",
        legend_title="Former Enslavement Status",
        font=dict(
            family="Segoe UI",
            size=16)
    )

    fig6 = px.scatter(df, x="PersonTaxLeviedLand", y="PersonTaxStateAll",
            color="FormerlyEnslaved",
            color_discrete_sequence=px.colors.qualitative.Antique,
            width=800, height=500)
    
    fig6.update_layout(
        title={'text':"Amount Taxed on Land vs. Total Tax Value by Former Enslavement Status",
               'x':0.5,
               'xanchor': 'center'},
        xaxis_title="Total Tax on Land",
        yaxis_title="Total State Tax Amount",
        legend_title="Former Enslavement Status",
        font=dict(
            family="Segoe UI",
            size=16)
    )


    graphJSON = [None, None, None, None, None, None]
    graphJSON[0] = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON[1] = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON[2] = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON[3] = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON[4] = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON[5] = json.dumps(fig6, cls=plotly.utils.PlotlyJSONEncoder)
    
    print(fig1.data[0])
    print(fig2.data[0])
    print(fig3.data[0])
    print(fig4.data[0])
    print(fig5.data[0])
    print(fig6.data[0])
    
    #fig.data[0]['staticPlot']=True
    
    return graphJSON

# SIMPLE SEARCH -------------------------------------------------------------

@app.route("/simple_search", methods=['POST', 'GET']) # without methods, this page on its own will not exist
def simple_search():
    """
    Renders the main page; no cards/people for now
    Takes inputs: text search bars (given_name, surname), 
                  text/date selection (two for list type date_range)
                  text search bar (location)
                  dropdown (source)
    """

    columns = list(mongo.db["Tax_Record_1867"].find_one({}, {'_id':False}))
    
    # Takes in input from HTML
    given_name = request.form.get("given_name") 
        # assumes <input type="text" name="given_name" id="given_name" minlength="3" class="validate">
    surname = request.form.get("surname")
        # assumes <input type="text" name="surname" id="surname" minlength="3" class="validate">
    date_range_0 = request.form.get("date_range_0")
    date_range_1 = request.form.get("date_range_1")
    location = request.form.get("location")
    chosen_col = request.form.getlist("chosen_col")

    if "" in chosen_col:
        chosen_col.remove("")
    if len(chosen_col)==0:
        chosen_col = ['EventLocJurisdictionCounty', 'PersonGivenNames', 'PersonSurname', 'EventImageLink']
    chosen_col_dict = {}
    for col in chosen_col:
        chosen_col_dict[col] = 1
    chosen_col_dict['_id'] = 0
    
    if date_range_0 == "":
        date_range_0 = None

    if date_range_1 == "":
        date_range_1 = None

    if date_range_0 != None and date_range_1 != None:
        date_range_0 = int(date_range_0)
        date_range_1 = int(date_range_1)
        date_range = [date_range_0, date_range_1]
    else:
        date_range = []

    # SEARCH FUNCTION
    #----------------------------------------------

    # get column names
    keys = mongo.db['Tax_Record_1867'].find_one()

    # separate keys by type of information
    key_for_given_name = list()
    key_for_surname = list()
    key_with_date = list()
    key_with_location = list()

    for key in keys:

        # if column name is "EventTitle"
        if key=="EventTitle":
            key_for_given_name.append(key)
            key_for_surname.append(key)

        # if column name does not include "GivenNames" or "Surname" but includes "name"
        if (not "GivenNames" in key) and (not "Surname" in key) and ("name" in key.lower()):
            key_for_given_name.append(key)
            key_for_surname.append(key)

        # if column name includes "GivenNames"
        if ("GivenNames" in key):
            key_for_given_name.append(key)

        # if column name includes "Surname"
        if ("Surname" in key):
            key_for_surname.append(key)

        # if column name includes "date"
        if ("date" in key.lower()):
            key_with_date.append(key)

        # if column name includes "loc"
        if ("loc" in key.lower()):
            key_with_location.append(key)


    # build query

    query = {} 
    query["$and"] = []

    # add onto query with keys
    if given_name:
        given_name_query = {"$or" : []}
        for key in key_for_given_name:
            given_name_query["$or"].append({ key: {"$regex" : given_name, "$options" : "i"} })
        if given_name_query:
            query["$and"].append(given_name_query)

    if surname:
        surname_query = {"$or" : []}
        for key in key_for_surname:
            surname_query["$or"].append({ key: {"$regex" : surname, "$options" : "i"} })
        if surname_query:
            query["$and"].append(surname_query)

    if date_range:
        date_query = {"$or" : []}
        for key in key_with_date:
            date_query["$or"].append({ key: {'$gte' : date_range[0], '$lte' : date_range[1]} })
        if date_query:
            query["$and"].append(date_query)

    if location:
        location_query = {"$or" : []}
        for key in key_with_location:
            location_query["$or"].append({ key : {"$regex" : location, "$options" : "i"} })
        if location_query:
            query["$and"].append(location_query)

    # produce result
    if len(query['$and'])==0:
        output = pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({}, chosen_col_dict).limit(5)))
    elif pd.DataFrame(list(mongo.db["Tax_Record_1867"].find(query))).empty:
        output = pd.DataFrame(columns=list(mongo.db['Tax_Record_1867'].find_one({}, chosen_col_dict).keys()))
    else:
        output = pd.DataFrame(list(mongo.db["Tax_Record_1867"].find(query, chosen_col_dict).limit(40)))

    #----------------------------------------------
    # END SEARCH FUNCTION
    
    search_fig = ff.create_table(output)

    searchJSON = search_fig.to_json()
    
    return render_template(
        "simple_search.html",
        columns=columns,
        searchJSON=searchJSON,
        selected_given_name = given_name,
        selected_surname = surname,
        selected_date_0 = date_range_0,
        selected_date_1 = date_range_1,
        selected_location = location,
        selected_chosen_col = chosen_col
    )



# INTERACTIVE VISUALIZATION ----------------------------------------------

@app.route("/graph_interactive") # without methods, this page on its own will not exist
def graph_interactive():
    """
    Renders the main page; no cards/people for now
    Takes inputs: text search bars (given_name, surname), 
                  text/date selection (two for list type date_range)
                  text search bar (location)
                  dropdown (source)
    """

    return render_template(
        "graph_interactive.html",
        columns=columns
    )

@app.route("/graph", methods=["GET", "POST"])
def graph():

    var_1 = request.form.get("x_col")
    var_2 = request.form.get("y_col")
    var_3 = request.form.get("group_col")

    try:
        agg_func = request.form['agg_options']
    except KeyError:
        agg_func = None

    try:
        fig_type = request.form['fig_options']
    except KeyError:
        fig_type = None

    # data = pd.DataFrame(list(mongo.db["Tax_Record_1867"].find()))

    categoricals = ['SourceSteward', 'SourceLocCity', 'SourceLocState', 'SourceTitle',
               'SourceType', 'SourceDateYearCreated', 'SourceCreator',
               'SourceLocCreatedCounty', 'SourceAuthorName', 'EventTitle',
               'EventLocJurisdictionCounty', 'EventDateYear', 'EventTranscriberNotes',
               'PersonSurname', 'PersonGivenNames', 'PersonNameAlternate',
               'PersonNameSuffix', 'PersonEventRole', 'PersonFN', 'PersonRoleLocSurnameEmployer', 
                'PersonRoleGivenNamesEmployer',
               'PersonAlternateNameEmployer', 'PersonRoleNameSuffixEmployer',
               'PersonRoleLocEmployment', 'PersonRoleLocResidence','PersonTaxCommissionerRemarks', 'EventImageLink']

    # start by specifying which type of visualization the user wants
    # if they don't say, prompt them to specify
    if fig_type == None or fig_type == '':
        error = 'Please specify a visualization type to continue.'
        
    # if they want a bar chart
    elif fig_type == 'bar':
        # if var_1 isn't specified
        if var_1 == None or var_1 == "":
            error = 'Please specify at least an x-value variable to create a bar chart.'
        # if var_1 isn't categorical - need to hardcode, add in here
        elif var_1 not in categoricals:
            error = 'Please specify a categorical x-value variable, not a numeric one.'
        # if var_1 is specified
        else:
            # if they don't specify an agg_func or if it's count
            if agg_func == None or agg_func == "" or agg_func == 'count':
                # if they specify variable 3
                if var_3 != None and var_3 != "":
                    # if they give variables 1 and 2
                    if var_2 != None and var_2 != "":
                        # if variable 2 isn't numeric
                        if var_2 in categoricals:
                            error = 'Please specify a numeric y-value variable, not a categorical one.'
                        # if it is, proceed
                        else:
                            new_data = pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                            {var_1:1, var_2:1, var_3:1, '_id':0}))) # data[[var_1, var_2, var_3]]
                            fig = px.bar(new_data, x=var_1, y=var_2, color=var_3,
                                    color_discrete_sequence=px.colors.qualitative.Antique,
                                    hover_name=var_2,
                                    height=600, width=1000)
                    # if they only give variable 1
                    else:
                        new_data = pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                            {var_1:1, var_3:1, '_id':0}))) # data[[var_1, var_3]]
                        fig = px.bar(new_data, x=var_1, color=var_3,
                                color_discrete_sequence=px.colors.qualitative.Antique,
                                hover_name=var_3,
                                height=600, width=1000)
                # if they don't specify variable 3
                else:
                    # if they give variables 1 and 2
                    if var_2 != None and var_2 != "":
                        # if variable 2 isn't numeric
                        if var_2 in categoricals:
                            error = 'Please specify a numeric y-value variable, not a categorical one.'
                        # if it is, proceed
                        else:
                            new_data = pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                            {var_1:1, var_2:1, '_id':0}))) # data[[var_1, var_2]]
                            fig = px.bar(new_data, x=var_1, y=var_2,
                                    color_discrete_sequence=px.colors.qualitative.Antique,
                                    hover_name=var_2,
                                    height=600, width=1000)
                    # if they only give variable 1
                    else:
                        new_data = pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                            {var_1:1, '_id':0}))) # data[[var_1]]
                        fig = px.bar(new_data, x=var_1,
                                color_discrete_sequence=px.colors.qualitative.Antique,
                                hover_name=var_1,
                                height=600, width=1000)
            # if the agg_func is mean
            elif agg_func == 'mean':
                # if they specify variable 3
                if var_3 != None and var_3 != "":
                    # if they give variables 1 and 2
                    if var_2 != None and var_2 != "":
                        if var_2 in categoricals:
                            error = 'Please specify a numeric y-value variable, not a categorical one.'
                        # if it is, proceed
                        else:
                            new_data = pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                                {var_1:1, var_2:1, var_3:1, '_id':0})))\
                                            .groupby([var_1, var_3])\
                                                .agg({var_2:agg_func})\
                                                .reset_index()
                            fig = px.bar(new_data, x=var_1, y=var_2, color=var_3,
                                    color_discrete_sequence=px.colors.qualitative.Antique,
                                    hover_name=var_2,
                                    height=600, width=1000)
                    # if they only give variable 1
                    else:
                        error = 'Please specify a y-value variable to use the aggregation function "mean."'
                # if they don't specify variable 3
                else:
                    # if they give variables 1 and 2
                    if var_2 != None and var_2 != "":
                        # if variable 2 isn't numeric
                        if var_2 in categoricals:
                            error = 'Please specify a numeric y-value variable, not a categorical one.'
                        # if it is, proceed
                        else:
                            new_data = pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                            {var_1:1, var_2:1, '_id':0})))\
                                        .groupby(var_1)\
                                        .agg({var_2:agg_func})\
                                        .reset_index()
                            fig = px.bar(new_data, x=var_1, y=var_2,
                                    color_discrete_sequence=px.colors.qualitative.Antique,
                                    hover_name=var_2,
                                    height=600, width=1000)
                    # if they only give variable 1
                    else:
                        error = 'Please specify a y-value variable to use the aggregation function "mean."'
            # if the agg_func is median
            elif agg_func == 'median':
                # if they specify variable 3
                if var_3 != None and var_3 != "":
                    # if they give variables 1 and 2
                    if var_2 != None and var_2 != "":
                        # if variable 2 isn't numeric
                        if var_2 in categoricals:
                            error = 'Please specify a numeric y-value variable, not a categorical one.'
                        # if it is, proceed
                        else:
                            new_data = pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                            {var_1:1, var_2:1, var_3:1, '_id':0})))\
                                        .groupby([var_1, var_3])\
                                        .agg({var_2:agg_func})\
                                        .reset_index()
                            fig = px.bar(new_data, x=var_1, y=var_2, color=var_3,
                                    color_discrete_sequence=px.colors.qualitative.Antique,
                                    hover_name=var_2,
                                    height=600, width=1000)
                    # if they only give variable 1
                    else:
                        error = 'Please specify a y-value variable to use the aggregation function "median."'
                # if they don't specify variable 3
                else:
                    # if they give variables 1 and 2
                    if var_2 != None and var_2 != "":
                        # if variable 2 isn't numeric
                        if var_2 in categoricals:
                            error = 'Please specify a numeric y-value variable, not a categorical one.'
                        # if it is, proceed
                        else:
                            new_data = pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                            {var_1:1, var_2:1, '_id':0})))\
                                            .groupby(var_1)\
                                            .agg({var_2:agg_func})\
                                            .reset_index()
                            fig = px.bar(new_data, x=var_1, y=var_2,
                                    color_discrete_sequence=px.colors.qualitative.Antique,
                                    hover_name=var_2,
                                    height=600, width=1000)
                    # if they only give variable 1
                    else:
                        error = 'Please specify a y-value variable to use the aggregation function "median."'
   
    # if they want a scatterplot
    elif fig_type == 'scatter':
        # if var_1 isn't specified
        if var_1 == None or var_1 == "":
            error = 'Please specify an x-value variable to create a scatter plot.'
        # if var_1 isn't numeric
        elif var_1 in categoricals:
            error = 'Please specify a numeric x-value variable, not a categorical one.'
        # if var_1 is specified
        else:
            # note all agg_funcs work here, and don't change the code needed to plot the data
            # if they specify variable 3, variable 2 must be numeric
            if var_3 != None and var_3 != "":
                # if they give variables 1 and 2
                if var_2 != None and var_2 != "":
                    # if variable 2 isn't numeric
                    if var_2 in categoricals:
                        error = 'Please specify a numeric y-value variable, not a categorical one.'
                    # if it is, proceed
                    else:
                        new_data = pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                            {var_1:1, var_2:1, var_3:1, '_id':0}))) #data[[var_1, var_2, var_3]]
                        # if variable 3 is categorical
                        if var_3 in categoricals:
                            fig = px.scatter(new_data, x=var_1, y=var_2, color=var_3,
                                color_discrete_sequence=px.colors.qualitative.Antique,
                                hover_data=[var_1, var_2, var_3],
                                height=600, width=1000)
                        else:
                            fig = px.scatter(new_data, x=var_1, y=var_2, color=var_3,
                                color_continuous_scale=px.colors.sequential.turbid,
                                hover_data=[var_1, var_2, var_3],
                                height=600, width=1000)
                # if they only give variable 1
                else:
                    error = 'Please select at least an x-value variable and a y-value variable. If you only want to select one variable, consider a bar chart or table.'
            # if they don't specify variable 3, variable 2 can be categorical
            else:
                # if they give variables 1 and 2
                if var_2 != None and var_2 != "":
                    new_data = pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                            {var_1:1, var_2:1, '_id':0}))) # data[[var_1, var_2]]
                    fig = px.scatter(new_data, x=var_1, y=var_2,
                        color_discrete_sequence=px.colors.qualitative.Antique,
                        hover_data=[var_1, var_2],
                        height=600, width=1000)
                # if they only give variable 1
                else:
                    error = 'Please select at least an x-value variable and a y-value variable. If you only want to select one variable, consider a bar chart or table.'

    # if they want a table
    elif fig_type == 'tab':
        # if they specified an agg_func
        if agg_func != None and agg_func != "":
            # error = 'To create a table, don\'t select an aggregation function. If you want to use one, consider a bar chart or scatter plot.'
            if var_1 == None or var_1 == "" or var_2 == None or var_2 == "":
                error = 'To create a table with aggregation, specify an x-value variable and a y-value variable.'
            else:
                if var_3 == None or var_3 == '':
                    if var_2 not in categoricals:
                        fig = ff.create_table(pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                                {var_1:1, var_2:1, '_id':0})))\
                                                .groupby(var_1)\
                                                .agg({var_2:agg_func})\
                                                .reset_index())
                    else:
                        error = 'To create a table with aggregation, select a y-value variable that has numeric value.'
                else:
                    if var_1 not in categoricals:
                        error = 'To create a table with aggregation, select an x-value variable that has categorical value.'
                    elif var_3 not in categoricals:
                        error = 'To create a table with aggregation, select a groupby variable that has categorical value.'
                    elif var_2 in categoricals:
                        error = 'To create a table with aggregation, select a y-value variable that has numeric value.'
                    else:
                        fig = ff.create_table(pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                            {var_1:1, var_2:1, var_3:1, '_id':0})))\
                                            .groupby([var_1, var_3])\
                                            .agg({var_2:agg_func})\
                                            .reset_index())
        
        # if no agg_func
        else:
            # if var_1 doesn't exist
            if var_1 == None or var_1 == "":
                error = 'Please specify an x-value variable to create a table.'
            # if var_1 does exist
            else:
                # if var_2 doesn't exist
                if var_2 == None or var_2 == "":
                    # if var_3 doesn't exist
                    if var_3 == None or var_3 == "":
                        #fig=ff.create_table(data[[var_1]].sample(100))
                        fig = ff.create_table(pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                            {var_1:1, '_id':0}))).sample(100))
                    # if var_3 does exist
                    else:
                        # fig=ff.create_table(data[[var_1, var_3]].sample(100))
                        fig = ff.create_table(pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                            {var_1:1, var_3:1, '_id':0}))).sample(100))
                # if var_2 does exist
                else:
                    # if var_3 doesn't exist
                    if var_3 == None or var_3 == "":
                        # fig=ff.create_table(data[[var_1, var_2]].sample(100))
                        fig = ff.create_table(pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                            {var_1:1, var_2:1, '_id':0}))).sample(100))
                    # if var_3 does exist
                    else:
                        # fig=ff.create_table(data[[var_1, var_2, var_3]].sample(100))
                        fig = ff.create_table(pd.DataFrame(list(mongo.db["Tax_Record_1867"].find({},
                                            {var_1:1, var_2:1, var_3:1, '_id':0})).sample(100)))

    try:
        errorMessage = error
    except NameError:
        errorMessage = None

    try:
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    except NameError:
        graphJSON = None

    return render_template(
        "graph_interactive.html",
        columns=columns,
        graphJSON=graphJSON,
        errorMessage = errorMessage,
        selected_var1 = var_1,
        selected_var2 = var_2,
        selected_var3 = var_3,
        selected_agg = agg_func,
        selected_fig = fig_type
    )

# DATADICT --------------------------------------------------------------

@app.route("/data_dictionary") # without methods, this page on its own will not exist
def data_dictionary():

    data_dict = pd.DataFrame(list(mongo.db['Data_Dict']\
            .find({}, {'_id':False})))

    dict_fig = ff.create_table(data_dict)

    dict_fig.layout.width = 1250

    dictJSON = json.dumps(dict_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        "datadict.html",
        dictJSON=dictJSON
    )

# ERROR HANDLER ---------------------------------------------

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html")


# RUN --------------------------------------------------------

if __name__ == "__main__":
    app.run(# host=os.environ.get("IP"),
            port=9001, # int(os.environ.get("PORT"))
            debug=True)
# TO DO:
# - add CSS styling to the HTML for visuals, adding descriptions, etc.
# - fix callback function, add functionality for exploration and changing other graphs