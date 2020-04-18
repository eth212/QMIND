from django.contrib import admin
from django.conf.urls import url, include
from django.urls import path
from . import views

# The first path is just a reference to extend the urls.py of the WFApp folder.
# In the urls.py of the WFApp folder, "path('dashboard/', include('dashboard.urls'))" is seen.
# Therefore, the index.html file is accessed when adding 'dashboard/' to the url of the server.

# All the urls below are just the functions that are implemented in views.py. Any new functions in views.py must be referenced here.

"""
NOTE:

Typically, in the views.py file, functions will end with a return render(request, home.html), or something along
this line. Since there is no other page than index.html, the only function that returns index.html is the function called index.

Also, since no data is ever posted to the DB, only retrieved, all functions are called from JS scripts in the index.html files.
They are called with an AJAX .get() request, and the functions simply return a JSON data dump back to the JS script.

"""

urlpatterns = [
    path('', views.index, name='index'),
    url('getData', views.getData, name='getData'),
    url('getGoogleTrends', views.getGoogleTrends, name='getGoogleTrends'),
    url('updatetabledata', views.updatetabledata, name='updatetabledata'),
    url('populatedropdownsCat', views.populatedropdownsCat,
        name='populatedropdownsCat'),
    url('populatedropdownsDuty', views.populatedropdownsDuty,
        name='populatedropdownsDuty'),
    url('populatedropdownsMake', views.populatedropdownsMake,
        name='populatedropdownsMake'),
    url('populatedropdownsModel', views.populatedropdownsModel,
        name='populatedropdownsModel'),
    url('populatedropdowns', views.populatedropdowns, name='populatedropdowns'),
    url('updateSearchTerm1', views.updateSearchTerm1, name='updateSearchTerm1'),
    url('update_hist_data', views.update_hist_data, name='update_hist_data'),
    url('populate_dropdowns_location', views.populate_dropdowns_location,
        name='populate_dropdowns_location'),
    url('getSliderData', views.getSliderData, name='getSliderData'),
    # url('populatedropdownsMapYear', views.populatedropdownsMapYear,
    #     name='populatedropdownsMapYear')
    # url('update_hist_location_data', views.update_hist_location_data, name='update_hist_location_data'),
]
