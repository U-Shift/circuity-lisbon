import pandas as pd
import geopandas as gpd
from tqdm import tqdm, trange
import random
from shapely.geometry import Point, Polygon


def generate_random(number, polygon):
    points = []
    aux = polygon.bounds
    minx = aux['minx']
    miny = aux['miny']
    maxx = aux['maxx']
    maxy = aux['maxy']
    while len(points) < number:
        pnt = Point(random.uniform(float(minx), float(maxx)), random.uniform(float(miny), float(maxy)))
        if polygon.contains(pnt).any():
            points.append(pnt)
    return points

NUMBER_OF_POINTS_PER_ZONE = 5
OUTPUT_FILE = 'data/imob_generated_points.csv'

# Read IMOB data on OD

df = pd.read_csv('Data/IMOB/15.1_IMOB/BASE DADOS/AML/CSV/TBL_AML/TBL_viagens_OR_DE_AML.csv', sep=';')
df = df[df['DTCC_or11'].notna()]
df = df[df['DTCC_de11'].notna()]
df['DTCC_or11'] = df['DTCC_or11'].astype('int64')
df['FR_or11'] = df['FR_or11'].astype('int64')
df['Sec_or11'] = df['Sec_or11'].astype('int64')
df['SS_or11'] = df['SS_or11'].astype('int64')
df['DTCC_de11'] = df['DTCC_de11'].astype('int64')
df['FR_de11'] = df['FR_de11'].astype('int64')
df['Sec_de11'] = df['Sec_de11'].astype('int64')
df['SS_de11'] = df['SS_de11'].astype('int64')
df['Tipo_veiculo_2'] = df['Tipo_veiculo_2'].astype('category')

print('Original IMOB data shape: ', df.shape)

### Compute BRI for OD trips

df['BRI11_or'] = df['DTCC_or11'].astype('str').str.zfill(4) + \
                 df['FR_or11'].astype('str').str.zfill(2) + \
                 df['Sec_or11'].astype('str').str.zfill(3) + \
                 df['SS_or11'].astype('str').str.zfill(2)
df['BRI11_de'] = df['DTCC_de11'].astype('str').str.zfill(4) + \
                 df['FR_de11'].astype('str').str.zfill(2) + \
                 df['Sec_de11'].astype('str').str.zfill(3) + \
                 df['SS_de11'].astype('str').str.zfill(2)
df['BRI11_or'] = df['BRI11_or'].astype('int64')
df['BRI11_de'] = df['BRI11_de'].astype('int64')

### Filter for Lisbon municipaly instead of metropolitan area

mask_lisboa = (df['DTCC_or11'] == 1106) & (df['DTCC_de11'] == 1106)
df = df.loc[mask_lisboa]

print('Trips inside Lisbon\'s municipality:', df.shape[0])

# Divide into cycling, driving and walking trips

df_cycling = df[df['Tipo_veiculo_2'] == 'Cycling']
df_walking = df[df['Tipo_veiculo_2'] == 'Walking']
df_motorized = df[(df['Tipo_veiculo_2'] == 'passenger car - as driver') | \
                  (df['Tipo_veiculo_2'] == 'passenger car - as passenger') | \
                  (df['Tipo_veiculo_2'] == 'van/lorry/tractor/camper') | \
                  (df['Tipo_veiculo_2'] == 'Táxi (como passageiro)') | \
                  (df['Tipo_veiculo_2'] == 'motorcycle and moped')]
df_tp = df[(df['Tipo_veiculo_2'] == 'Regular train') | \
           (df['Tipo_veiculo_2'] == 'Urban rail') | \
           (df['Tipo_veiculo_2'] == 'Waterways') | \
           (df['Tipo_veiculo_2'] == 'bus and coach - TE') | \
           (df['Tipo_veiculo_2'] == 'bus and coach - TP')]
print('Amount of trips:',
      '\n  Cycling:', df_cycling.shape[0],
      '\n  Walking:', df_walking.shape[0],
      '\n  Motorized:', df_motorized.shape[0],
      '\n  TP:', df_tp.shape[0],)

# Read Lisbon's CAOP 2011 data
gdf = gpd.read_file("IMOB/lisboa2011/BGRI11_LISBOA.shp")

gdf['DTMN11'] = gdf['DTMN11'].astype('int64')
gdf['FR11'] = gdf['FR11'].astype('int64')
gdf['SEC11'] = gdf['SEC11'].astype('int64')
gdf['SS11'] = gdf['SS11'].astype('int64')
gdf['BGRI11'] = gdf['BGRI11'].astype('int64')
gdf['LUG11'] = gdf['LUG11'].astype('int64')

gdf_proj = gdf.to_crs(epsg=4326)

columns = ['point_A', 'point_B', 'vehicle', 'weekday', 'weight']

data = pd.DataFrame(columns=columns)

with tqdm(total=df.shape[0]*NUMBER_OF_POINTS_PER_ZONE) as t:
    t.set_description('Generating random points ')
    for i in range(df.shape[0]):
        example = df.iloc[i]
        example_or = example['BRI11_or']
        example_de = example['BRI11_de']

        mask_or = gdf_proj['BGRI11'] == example_or
        mask_de = gdf_proj['BGRI11'] == example_de

        example_or = gdf_proj.loc[mask_or]
        example_de = gdf_proj.loc[mask_de]

        for j in range(NUMBER_OF_POINTS_PER_ZONE):
            t.update(1)
            points_or = generate_random(1, example_or.geometry)[0]
            points_de = generate_random(1, example_de.geometry)[0]

            data_row = {}
            data_row['point_A'] = [points_or.x, points_or.y]
            data_row['point_B'] = [points_de.x, points_de.y]
            data_row['vehicle'] = example['Tipo_veiculo_2']
            data_row['weekday'] = example['Dia_da_semana']
            data_row['weight'] = example['PESOFIN']

            data = data.append(data_row, ignore_index=True, sort=False)

data.to_csv(OUTPUT_FILE)




