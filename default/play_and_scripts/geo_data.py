import rasterio

src = rasterio.open('default/play_and_scripts/Landsat_ETM_2001-08-26_multispectral.tif')
print(src.transform)