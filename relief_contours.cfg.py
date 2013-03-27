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
themedir = './themes/Terrain'
exportdir = os.path.join(themedir, 'cache', 'export')
cachedir = os.path.join('/tmp', tag, 'cache')
cachedir = os.path.join(themedir, 'cache')



# ============================================================================
# Land terrain relief

azimuth = 325

#    0   1   2   3   4   5   6   7   8   9  10  11
land_zfactors = \
    [100, 90, 80, 50, 40, 20, 16, 12, 9, 7,  6,  5]

land_zfactors_half = map(lambda x: x/2., land_zfactors)

elev_1km = os.path.join(datadir, 'srtm30_new/world_tiled.tif')
elev_100m = os.path.join(datadir, '_processed/world_3857.tif')
elev_10m = os.path.join(datadir, '_processed/ned/usmainland.vrt')

land_elevations = \
	[elev_1km, elev_1km, elev_1km, elev_1km, elev_1km, elev_1km, elev_1km,
	 elev_100m, elev_100m, elev_100m , elev_100m,
	 elev_10m]

land_elevation = dict(\
    prototype='node.raster',
    dataset_path=land_elevations,
    keep_cache=False,
    cache=dict(prototype='metacache',
               root=os.path.join(cachedir, 'land_elevation'),
               compress=False,
               data_format='gtiff',
        ),
    )

land_diffuse = dict(\
    prototype='node.hillshading',
    sources='land_elevation',
    zfactor=land_zfactors,
    scale=1,
    altitude=35,
    azimuth=azimuth,
    )

land_detail = dict(\
    prototype='node.hillshading',
    sources='land_elevation',
    zfactor=land_zfactors_half,
    scale=1,
    altitude=65,
    azimuth=azimuth,
)

land_specular = dict(\
    prototype='node.hillshading',
    sources='land_elevation',
    zfactor=land_zfactors,
    scale=1,
    altitude=85,
    azimuth=azimuth,
    )

land_cover = dict(\
    prototype='node.raster',
    dataset_path=os.path.join(datadir, 'natural-earth-2.0b3/raster/NE2_HR_LC/NE2_HR_LC.tiled.tif'),
#    dataset_path=os.path.join(datadir, 'natural-earth-2.0b3/raster/HYP_HR/HYP_HR_tiled.tif'),
#     dataset_path=os.path.join(datadir, '_processed/landcover-rgb-4326.tif'),
    )

land_relief = dict(
    prototype='node.imagemagick',
    sources=['land_diffuse', 'land_detail', 'land_specular', 'land_cover'],
    format='jpg',
    command='''
    (
          ( {{land_diffuse}} -fill grey50 -colorize 100%% )
          ( {{land_diffuse}} ) -compose blend -define compose:args=30%% -composite
          ( {{land_detail}} -fill #0055ff -tint 70 -gamma 0.8  ) -compose blend -define compose:args=40%% -composite
          ( {{land_specular}} -gamma 2 -fill #ffcba6 -tint 120 ) -compose blend -define compose:args=30%% -composite
          -brightness-contrast -10%%x-5%%
          ( {{land_cover}} -brightness-contrast -15%%x-7%% -modulate 100,100,96 %(blur)s ) -compose Overlay -composite
 	  -quality 100
    )
    ''',
    command_params=dict(
    	blur=['-blur 3', '-blur 3', '-blur 2', '-blur 2', '-blur 2', '-blur 1', '']
    	)
    )


# ============================================================================
# Bathymetry relief

#    0   1   2   3   4   5   6   7   8   9  10
bathymetry_zfactors = \
   [35, 30, 30, 25, 15,  10, 7,  4,  3,  2,  1]

bathymetry_zfactors_half = map(lambda x: x/2., bathymetry_zfactors)

bathymetry_elevation = dict(\
    prototype='node.raster',
    dataset_path=elev_1km,
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
    '''
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
    scale_factor=tile_size//256
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

labels = dict(\
    prototype='node.mapnik',
    theme=os.path.join(themedir, 'labels.xml'),
    image_type='png',
    buffer_size=tile_size,
    scale_factor=tile_size//256
    )


labels_halo = dict(\
    prototype='node.mapnik',
    theme=os.path.join(themedir, 'labels_halo.xml'),
    image_type='png',
    buffer_size=tile_size,
    scale_factor=tile_size//256
    )


# ============================================================================
# Final composer

composer = dict(
    prototype='node.imagemagick',
    sources=['land_relief',
#     		 'relief_contours',
     		 'builtup_area', 'waterbody',
		 'bathymetry_relief', 'ocean_mask',
		 'roads', 'labels_halo'
            ],
    format='jpg',
    command='''
    (
        #### Land ####
 	(
 	    {{land_relief}} -gamma %(land_gamma)s -sigmoidal-contrast 2.2 -sharpen 0x0.7
        )

#        {{relief_contours}} -compose multiply -composite
        {{builtup_area}} -compose lighten -composite
        {{waterbody}}
        -compose over -composite

        #### Bathymetry ####
        ( {{bathymetry_relief}} {{ocean_mask}} -compose copyopacity -composite ) -compose over -composite

 		#### Roadmap ####
        ( {{roads}}
        ) -compose over -composite

        ( {{labels_halo}} -geometry +0+1
          -channel A -blur 4 -evaluate multiply %(shadow_intensity)s +channel
          -channel rgb -evaluate set 0 +channel
        ) -compose multiply -composite

        ( {{labels_halo}} +level 0%%x%(halo_lightness)s%% ) -compose over -composite

         -quality 90
    )
    ''',
    command_params=dict(
                         #   0     1     2     3     4     5     6     7     8     9   10   11   12   13
    	land_gamma=      [0.62, 0.63, 0.64, 0.66, 0.67, 0.72, 0.77, 0.81, 0.86, 0.86, 0.9, 0.9, 0.9, 1.0],
    	halo_lightness=  [  80,   80,   80,   80,   80,   85,   90,   95,  100],
    	shadow_intensity=[0.0 ,  0.0,  0.0,  0.0,  0.0,  0.1, 0.15, 0.23,  0.3, 0.35],
    	)
    )

ROOT = dict(\
    renderer='composer',
    metadata=dict(tag=tag,
                  version='1.1',
                  description='High Quality Shaded Relief Map',
                  attribution='OSM, SRTM+, NED',
                  ),

    storage=dict(prototype='cluster',
                 stride=16,
                 servers=['localhost:11211',],
                 root=os.path.join(exportdir, '%s' % tag),
                 ),

    pyramid=dict(levels=range(0, 17),
#                 envelope=[-127,27,-67,50], # US mainland
#                 envelope=[-93,27,-67,50], # US mainland
#                 envelope=[-159,20,-154,22], # US Hawaii
# 				 envelope=[-122.4475, 37.7879,-122.4474, 37.7880],
                 zoom=7,
                 center=(-122.4475, 37.7879),
                 format=fmt,
                 buffer=32,
                 tile_size=tile_size,
                 ),
)

