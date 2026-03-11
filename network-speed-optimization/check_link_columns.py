import geopandas as gpd
gdf = gpd.read_file(r'H:\go\network_builder\inputs\net_export\netexport_link.shp')
print('Colonne:', list(gdf.columns))
print('Righe:', len(gdf))
has_no = 'NO' in gdf.columns
print('Ha colonna NO (link id):', has_no)
cols = ['FROMNODENO','TONODENO','TYPENO'] + (['NO'] if has_no else [])
print(gdf[cols].head(5).to_string())
