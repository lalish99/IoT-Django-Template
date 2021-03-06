from matplotlib.backends.backend_agg import FigureCanvasAgg
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, Http404
from django.template import loader
from django.urls import reverse
from IoT import models
import IoT.model_choices as choices
import matplotlib.pyplot as plt
import io


def project_sensors(project_id):
    """
    Find all sensors in project
    """
    project = get_object_or_404(models.Projects, pk=project_id)
    sensors = []
    for z in project.project_zones.all():
        sensors.extend(z.zone_ambiental_sensors.all())
        for n in z.zone_nodes.all():
            sensors.extend(n.node_sensors.all())
    
    return sensors


def sensor_graph(request, project_id, sensor_id):
    """
    Plots all measurements from a sensor
    ====

    This view loads all measurements from a sensor and
    groups the different measurement types of the 
    selected sensor which then are plotted in a 
    matplotlib plot and transformed to an image to
    return it
    """
    sensor = get_object_or_404(models.Sensors, pk=sensor_id)
    if sensor not in project_sensors(project_id):
        raise PermissionDenied()

    measures = list()
    for m_type in [x for x,v in choices.MEASUREMENT_TYPE_CHOICES]:
        measurements = sensor.sensor_measurements.values_list('value','created_at')
        measurements = measurements.filter(measurement_type=m_type)
        if measurements:
            values, dates = zip(*measurements)
            measures.append(({k:v for k,v in choices.MEASUREMENT_TYPE_CHOICES}[m_type], values, dates))
    # Count unique lenghts of values
    d = []
    d = set([len(l) for (x,l,m) in measures if len(l) not in d])
    # Create figure and axes
    f, a =  plt.subplots(len(d),1,figsize=(10,(5*len(d))))
    f.suptitle({k:v for k,v in choices.SENSOR_TYPE_CHOICES}[sensor.sensor_type], fontsize=16)
    if len(d) > 1:
        # Loop same lenght values
        for i, l in enumerate(d):
            same = [x for x in measures if len(x[1]) == l]
            for values in same:
                # Plot
                a[i].plot(values[2],values[1],label=values[0])
                a[i].legend()
    else:
        for values in measures:
            # Plot
            a.plot(values[2],values[1],label=values[0])
            a.legend()

    f.autofmt_xdate()
    # Byte information
    buf = io.BytesIO()
    canvas = FigureCanvasAgg(f)
    canvas.print_png(buf)
    # Format response
    response = HttpResponse(buf.getvalue(), content_type='image/png')
    response['Content-Length'] = str(len(response.content))
    # Clear figure to save space
    f.clear()
    return response


def graph(request, project_id, sensor_id, measurement_type):
    """
    Plots graph of one meassurment type from a sensor
    ====

    This view loads all the meassurments of one type from 
    a sensor and plots it in a matplotlib graph which is 
    then transformed into an image and returned
    """
    sensor = get_object_or_404(models.Sensors, pk=sensor_id)
    if sensor not in project_sensors(project_id):
        raise PermissionDenied()

    measurements = sensor.sensor_measurements.values_list('value','created_at')
    measurements = measurements.filter(measurement_type=measurement_type)
    # Missing date filtering and authentication
    values, dates = zip(*measurements)
    f, ax = plt.subplots(figsize=(10,10))
    ax.plot(dates, values)
    ax.set_title({k:v for k,v in choices.MEASUREMENT_TYPE_CHOICES}[measurement_type])
    f.autofmt_xdate()
    # Byte information
    buf = io.BytesIO()
    canvas = FigureCanvasAgg(f)
    canvas.print_png(buf)
    # Format response
    response = HttpResponse(buf.getvalue(), content_type='image/png')
    response['Content-Length'] = str(len(response.content))
    # Clear figure to save space
    f.clear()
    return response


def graph_mixed(request, project_id, zone_id, measurement_type):
    """
    Plots graphs of all same measurement types in zone
    ====

    This view loads all sensors that have a similar measurement 
    type from a specified zone and then plots the results in a
    matplotlib graph which is then transformed into an image and
    returned

    In case some sensors have less measurement than others they
    are separated into different subplots
    """
    zone = get_object_or_404(models.Zones, pk=zone_id)
    project = get_object_or_404(models.Projects, pk=project_id)
    if zone not in project.project_zones.all():
        raise PermissionDenied()

    sensors = zone.zone_ambiental_sensors.filter(ambiental=True)
    measures = list()
    for sensor in sensors:
        measurements = sensor.sensor_measurements.values_list('value','created_at')
        measurements = measurements.filter(measurement_type=measurement_type)
        if measurements:
            values, dates = zip(*measurements)
            measures.append((sensor.sensor_type, values, dates))
    # Missing date filtering and authentication
    # Count unique lenghts of values
    d = []
    d = set([len(l) for (x,l,m) in measures if len(l) not in d])
    # Create figure and axes
    f, a =  plt.subplots(len(d),1,figsize=(10,(5*len(d))))
    # Loop same lenght values
    for i, l in enumerate(d):
        same = [x for x in measures if len(x[1]) == l]
        for values in same:
            # Plot
            a[i].set_title({k:v for k,v in choices.MEASUREMENT_TYPE_CHOICES}[measurement_type])
            a[i].plot(values[2],values[1],label=values[0])
            a[i].legend()

    f.autofmt_xdate()
    # Byte information
    buf = io.BytesIO()
    canvas = FigureCanvasAgg(f)
    canvas.print_png(buf)
    # Format response
    response = HttpResponse(buf.getvalue(), content_type='image/png')
    response['Content-Length'] = str(len(response.content))
    # Clear figure to save space
    f.clear()
    return response