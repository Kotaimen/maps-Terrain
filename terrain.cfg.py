# ============================================================================
# Terrain Render Configuration File
# ============================================================================

version = 0.95

import os

# ============================================================================
# Global variables

tag = 'Terrain'
tile_size = 256
fmt = 'jpg'
scalefactor = 1

datadir = '/Users/Kotaimen/proj/geodata'
themedir = './themes/Terrain_1305'
exportdir = os.path.join(themedir, 'cache', 'export')
cachedir = os.path.join(themedir, 'cache')


# ============================================================================
# Relief data path
azimuth = 325

srtm30_new = os.path.join(datadir, 'srtm30_new/world_tiled.tif')
srtm30_org = os.path.join(datadir, 'SRTM_30_org/world_filled/')
ned100 = os.path.join(datadir, 'DEM-Tools-patch/source/ned100m/')
ned10 = os.path.join(datadir, 'DEM-Tools-patch/source/ned10m_3857/')
ned3 = os.path.join(datadir, 'DEM-Tools-patch/source/ned3m/')

# ============================================================================
# Bathymetry relief, using GDAL engine

#    0   1   2   3   4   5   6   7   8   9  10
bathymetry_zfactors = \
   [35, 30, 30, 25, 15,  10, 7,  4,  3,  2,  1]

bathymetry_zfactors_half = map(lambda x: x/2., bathymetry_zfactors)

bathymetry_elevation = dict(\
    prototype='node.raster',
    dataset_path=srtm30_new,
    keep_cache=False,
    cache=dict(prototype='metacache',
               root=os.path.join(cachedir, 'bathymetry_elevation'),
               compress=False,
               data_format='gtiff',
        ),
    )

bathymetry_hypsometricmap = dict(\
    prototype='node.colorrelief',
    cache=None,
    sources='bathymetry_elevation',
    color_context=os.path.join(themedir, 'hypsometric-map-ocean.txt'),
    )

bathymetry_diffuse = dict(\
    prototype='node.hillshading',
    sources='bathymetry_elevation',
    zfactor=bathymetry_zfactors,
    scale=1,
    altitude=35,
    azimuth=azimuth,
    )

bathymetry_detail = dict(\
    prototype='node.hillshading',
    sources='bathymetry_elevation',
    zfactor=bathymetry_zfactors_half,
    scale=1,
    altitude=65,
    azimuth=azimuth,
)

bathymetry_specular = dict(\
    prototype='node.hillshading',
    sources='bathymetry_elevation',
    zfactor=bathymetry_zfactors,
    scale=1,
    altitude=85,
    azimuth=azimuth,
    )

bathymetry_relief = dict(\
    prototype='node.imagemagick',
    sources=['bathymetry_diffuse', 'bathymetry_detail', 'bathymetry_specular', 'bathymetry_hypsometricmap'],
    format='jpg',
    command='''
    (
         ( {{bathymetry_diffuse}} -fill grey50 -colorize 100%% )
         ( {{bathymetry_diffuse}} ) -compose blend -define compose:args=30%% -composite
         ( {{bathymetry_detail}} -fill #4C78FF -tint 80 -gamma 0.8  ) -compose blend -define compose:args=40%% -composite
         ( {{bathymetry_specular}} -gamma 3 ) -compose blend -define compose:args=30%% -composite
         -brightness-contrast -10%%x-5%%
         ( {{bathymetry_hypsometricmap}} ) -compose overlay -composite
 		 -quality 100
    )
    ''',
    cache=dict(prototype='metacache',
               root=os.path.join(cachedir, 'bathymetry_relief'),
               compress=False,
               data_format='jpg',
        ),
    )


# ============================================================================
# Land terrain relief, using homebrew blending engine

land_hillshading = dict(\
    prototype='node.homebrewhillshade',
    dataset_path=[
                  srtm30_new, #0
                  srtm30_new, #1
                  srtm30_new, #2
                  srtm30_new, #3
                  srtm30_new, #4
                  srtm30_new, #5
                  srtm30_new, #6
                  [srtm30_org, srtm30_new], #7
                  [srtm30_org, srtm30_new], #8
                  [srtm30_org, srtm30_new], #9
                  [srtm30_org, srtm30_new], #10
                  [ned10, srtm30_org], #11
                  [ned10, srtm30_org], #12
                  [ned10, srtm30_org], #13
                  [ned10, srtm30_org], #14
                  ned10,
#                  [ned10, srtm30_org], #15
                  [ned3, ned10], #16
                  ],
    #          0  1    2    3  4    5  6   7   8  9 10 11
    zfactor=[100, 90, 80, 50, 40, 20, 16, 13, 10, 8, 6, 5],
    scale=1,
    azimuth=azimuth,
    cache=dict(prototype='metacache',
               root=os.path.join(cachedir, 'land_relief'),
               compress=False,
               data_format='jpg',
        ),
    )

labels_halo = dict(\
    prototype='node.mapnik',
    theme=os.path.join(themedir, 'labels_halo.xml'),
    image_type='png',
    buffer_size=tile_size,
    scale_factor=tile_size//256
    )

land_cover = dict(\
    prototype='node.raster',
    dataset_path=os.path.join(datadir, 'natural-earth-2.0b3/raster/NE2_HR_LC_2/NE2_HR_LC_3857.tif'),
#    dataset_path=os.path.join(datadir, 'natural-earth-2.0b3/raster/HYP_HR/HYP_HR_tiled.tif'),
#    dataset_path=os.path.join(datadir, '_processed/landcover-rgb-4326.tif'),
    )

land_relief = dict(
    prototype='node.imagemagick',
    sources=['land_hillshading', 'land_cover', 'labels_halo'],
    format='jpg',
    command='''
    (

      ( {{land_hillshading}} -brightness-contrast -10%%x-3%% )

      ( {{land_hillshading}} -brightness-contrast +4%%x-37%%
        {{labels_halo}} -compose copyopacity -composite  ) -compose Over -composite
      ( {{land_cover}} -brightness-contrast -13%%x-5%% -modulate 100,100,95 %(blur)s  ) -compose Overlay -composite
      -quality 100
    )
    ''',
    command_params=dict(
    	blur=['-blur 3', '-blur 3', '-blur 2', '-blur 2', '-blur 2', '-blur 1', '']
    	),
    )



# ============================================================================
# Landmass, Waterbody masks

ocean_mask = dict(\
    prototype='node.mapnik',
    theme=os.path.join(themedir, 'watermask.xml'),
    image_type='png',
    buffer_size=0,
    scale_factor=1
    )

builtup_area = dict(\
    prototype='node.mapnik',
    theme=os.path.join(themedir, 'builtuparea.xml'),
    image_type='png',
    buffer_size=tile_size//4,
    scale_factor=tile_size//256
    )

waterbody = dict(\
    prototype='node.mapnik',
    theme=os.path.join(themedir, 'waterbody.xml'),
    image_type='png',
    buffer_size=0,
    scale_factor=tile_size//256
    )

relief_contours = dict(\
    prototype='node.mapnik',
    theme=os.path.join(themedir, 'contours.xml'),
    image_type='png',
    buffer_size=tile_size//2,
    scale_factor=tile_size//256,
    cache=dict(prototype='metacache',
               root=os.path.join(cachedir, 'contours'),
               compress=False,
               data_format='png',
        ),
    )

# ============================================================================
# Roads & labels

roads = dict(\
    prototype='node.mapnik',
    theme=os.path.join(themedir, 'roads.xml'),
    image_type='png',
    buffer_size=0,
    scale_factor=tile_size//256
    )

boundary = dict(\
    prototype='node.mapnik',
    theme=os.path.join(themedir, 'boundary.xml'),
    image_type='png',
    buffer_size=0,
    scale_factor=tile_size//256
    )

labels = dict(\
    prototype='node.mapnik',
    theme=os.path.join(themedir, 'labels.xml'),
    image_type='png',
    buffer_size=tile_size,
    scale_factor=tile_size//256
    )


# ============================================================================
# Composing

composer = dict(
    prototype='node.imagemagick',
    sources=['land_hillshading', 'land_cover',
             'labels_halo',
      	     'bathymetry_relief', 'ocean_mask',
#             'relief_contours',
     	     'builtup_area',
             'waterbody',
             'roads', 'boundary', 'labels',
             ],
    format='jpg',
    command='''
    (
        #### Landmass with color relief ####
        (
             ( {{land_hillshading}} -brightness-contrast -10%%x-3%% )
             ## Smart halo by fill with low contrast
             (
                {{land_hillshading}} -brightness-contrast +5%%x-34%%
                {{labels_halo}} -compose CopyOpacity -composite
             ) -compose Over -composite
             (
                 {{land_cover}} -brightness-contrast -13%%x-5%%
                 -modulate 100,100,95 %(blur_radius)s
             ) -compose Overlay -composite
             -sharpen 0x0.8
             -gamma %(land_gamma)s
             -sigmoidal-contrast 2.2
        )

        #### Contours ####
#        (
#             {{relief_contours}}
#             ## Smart halo by knock out
#             ( {{labels_halo}} ) -compose Dst-out -composite
#        )
#        -compose Multiply -composite

        #### Land overlay ####
        {{builtup_area}} -compose Lighten -composite
        {{waterbody}} -compose Over -composite

        #### Bathymetry overlay ####
        (
           {{bathymetry_relief}}
           {{ocean_mask}} -compose CopyOpacity -composite
        ) -compose Over -composite

        #### Roadmap ####
        (
            {{roads}} -channel rgb -gamma 0.9 +level 0%%x85%% +channel
            ( {{labels_halo}} ) -compose Dst-out -composite
        ) -compose Hard_Light -composite

        {{boundary}} -compose Over -composite

        ( {{labels}}  +level %(label_intensity)s%%x90%% ) -compose over -composite

        -quality 90
    )
    ''',
    command_params=dict(
                         #       1          2          3          4          5          6
        blur_radius=     ['-blur 3', '-blur 3', '-blur 2', '-blur 2', '-blur 2', '-blur 1', ''],
                         #   0     1     2     3     4     5     6     7     8     9   10   11   12   13
    	land_gamma=      [0.67, 0.67, 0.67, 0.70, 0.71, 0.72, 0.77, 0.81, 0.86, 0.86, 0.9, 0.9, 0.9, 1.0],
        label_intensity= [0   ,    0,    0,    0,    2,    3,    5,    6,    7,   10],
    	),
    )

# ============================================================================
# ROOT

ROOT = dict(\
    renderer='composer',
    metadata=dict(tag=tag,
                  version='1.3',
                  description='High Quality Shaded Relief Map',
                  attribution='OSM, SRTM+, NED',
                  ),

storage=dict(prototype='cluster',
             stride=16,
             servers=['localhost:11211',],
             root=os.path.join(exportdir, '%s_smarthalo' % tag),
             ),

    pyramid=dict(levels=range(0, 16),
#                 envelope=[-127,27,-67,50], # US mainland
#                 envelope=[-93,27,-67,50], # US mainland
#                 envelope=[-159,18,-154,22], # US Hawaii
# 				 envelope=[-122.4475, 37.7879,-122.4474, 37.7880],
                 zoom=7,
                 center=(-122.4475, 37.7879),
                 format=fmt,
                 buffer=32,
                 tile_size=tile_size,
                 ),
)

