# A circuity temporal analysis of urban street networks using open data: a Lisbon case study




### Abstract

Urban street networks impact urban space usage and movement across a city. Circuity, the 
ratio of network distances to straight-line distances, is considered a critical 
measurement in urban network morphology and transportation efficiency as it can measure 
the attractiveness of routes in terms of distance traveled. Here, we compare circuity 
measures for drivable, cyclable, and walkable networks to analyze how they evolved and 
understand whether urban changes have produced meaningful circuity changes. Our analyses 
rely on Lisbon data from OpenStreetMaps to explore circuity for the period 2013-2020, 
which we used to simulate 4.8 million routes using OpenRouteService to compute the 
different modes' circuity measures. Our findings suggest that it is crucial to analyze 
each transport network type separately when planning or modeling urban street networks. 
Their composition and design differ significantly from mode to mode, such as their 
attractiveness to users. We identify significant changes in modes' circuity over time, 
especially in cycling, following Lisbon's cycling infrastructure expansion. Our paper 
demonstrates that the circuity indicator is useful when planning and modeling street 
networks, in particular, to optimize the location choice for interventions required to 
increase the attractiveness of active modes and promote sustainable mobility. At the 
same time, we emphasize the lack of information on walking infrastructures required for 
more detailed analyses.


## Usage

1. Main (circuity) analysis ([01-circuity_analysis.ipynb](01-circuity_analysis.ipynb))
2. Inequalities analysis ([02-inequalities-gini.ipynb](02-inequalities-gini.ipynb))
3. Waytypes analysis ([03-routes-waytypes.ipynb](03-routes-waytypes.ipynb))
4. Lisbon's cycleways ([04-lisbon-cicleways.ipynb](04-lisbon-cicleways.ipynb))
5. Lisbon's road network length ([05-osm_data_road_length.ipynb](05-osm_data_road_length.ipynb))

If you wish to generate points and compute routes:

1. Dowload OSM data for the Lisbon area 
2. Setup a [OpenRouteService](https://github.com/GIScience/openrouteservice) server
3. Setup the Random Sampling (RS) points and compute their routes ([RS_points_routes.py](RS_points_routes.py))
4. Setup the Mobility Survey Sampling (MSS) based points and compute their routes ([MSS_points.py](MSS_points.py) & 
[MSS_routes.py](MSS_routes.py))


### License

Our code is under [MIT license](LICENSE).


### Citation

If you find this project useful for your research, please use the following BibTeX entry.

```
@article{costa2021circuity,
    AUTHOR = {Costa, Miguel and Marques, Manuel and Moura, Filipe},
    TITLE = {A Circuity Temporal Analysis of Urban Street Networks Using Open Data: A Lisbon Case Study},
    JOURNAL = {ISPRS International Journal of Geo-Information},
    VOLUME = {10},
    YEAR = {2021},
    NUMBER = {7},
    ARTICLE-NUMBER = {453},
    URL = {https://www.mdpi.com/2220-9964/10/7/453},
    ISSN = {2220-9964},
    DOI = {10.3390/ijgi10070453}
}
```









