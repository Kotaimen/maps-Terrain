import os


zfactor = 8 #12 8 6 4
azimuth = 325
datadir = '/Users/Kotaimen/proj/geodata'
themedir= './themes/Terrain'
cachedir_export= os.path.join(themedir, 'cache')
tag = 'Terrain'
tile_size = 256
fmt = 'jpg'

cachedir=os.path.join('/tmp', tag, 'cache')

# ============================================================================
# Elevation Data Sources

elev_1km = dict(\
    prototype='datasource.dataset',
    dataset_path=os.path.join(datadir, 'srtm30_new/world_tiled.tif'),
    keep_cache=False,
    cache=dict(prototype='metacache',
        root=os.path.join(cachedir, 'elevation'),
        compress=False,
        data_format='gtiff',
        ),
    )

elev_100m = dict(\
    prototype='datasource.dataset',
    dataset_path=os.path.join(datadir, '/data/tilestorage/geodata/ned/all-100m.tif'),
    keep_cache=False,
    cache=dict(prototype='metacache',
        root=os.path.join(cachedir, 'elevation'),
        compress=False,
        data_format='gtiff',
        ),
    )

elev_30m = dict(\
    prototype='datasource.dataset',
    dataset_path=os.path.join(datadir, 'SRTM_30_org/world/world_3857.tif'),
    keep_cache=False,
    cache=dict(prototype='metacache',
        root=os.path.join(cachedir, 'elevation'),
        compress=False,
        data_format='gtiff',
        ),
    )

elev_10m = dict(\
    prototype='datasource.dataset',
#    dataset_path=os.path.join(datadir, '/data/tilestorage/geodata/ned/usmainland.vrt'),
    dataset_path=os.path.join(datadir, '/data/tilestorage/geodata/ned/useast.tif'),
    keep_cache=False,
    cache=dict(prototype='metacache',
        root=os.path.join(cachedir, 'elevation'),
        compress=False,
        data_format='gtiff',
        ),
    )

elevation = dict(\
    prototype='composite.selector',
    sources = ['elev_1km', 'elev_30m', 'elev_10m'],
    #            0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18
    condition = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3],
    )

# ============================================================================
# Land shaded relief

    
diffuse = dict(\
    prototype='processing.hillshading',
    sources='elevation',
    zfactor=zfactor,
    scale=1,
    altitude=35,
    azimuth=azimuth,
    )

detail = dict(\
    prototype='processing.hillshading',
    sources='elevation',
    zfactor=zfactor / 2.,
    scale=1,
    altitude=65,
    azimuth=azimuth,
)

specular = dict(\
    prototype='processing.hillshading',
    sources='elevation',
    zfactor=zfactor,
    scale=1,
    altitude=85,
    azimuth=azimuth,
    )

# ============================================================================
# Land mapnik styles

landcover = dict(\
    prototype='datasource.dataset',
    dataset_path=os.path.join(datadir, 'natural-earth-2.0b3/raster/NE2_HR_LC/NE2_HR_LC.tiled.tif'),
    )

waterbody = dict(\
    prototype='datasource.mapnik',
    theme=os.path.join(themedir, 'waterbody.xml'),
    image_type='png',
    buffer_size=0,
    scale_factor=tile_size//256
    )

roads = dict(\
    prototype='datasource.mapnik',
    theme=os.path.join(themedir, 'roads.xml'),
    image_type='png',
    buffer_size=0,
    scale_factor=tile_size//256
    )

labels = dict(\
    prototype='datasource.mapnik',
    theme=os.path.join(themedir, 'labels.xml'),
    image_type='png',
    buffer_size=tile_size,
    scale_factor=tile_size//256
    )

# ============================================================================
# Bathymetry

bathymetry_zfactor = 3 # 5 4 3

colorrelief = dict(\
    prototype='processing.colorrelief',
    cache=None,
    sources='elev_1km',
    color_context=os.path.join(themedir, 'hypsometric-map-ocean.txt'),
    )

bathymetry_diffuse = dict(\
    prototype='processing.hillshading',
    sources='elev_1km',
    zfactor=bathymetry_zfactor,
    scale=1,
    altitude=35,
    azimuth=azimuth,
    )

bathymetry_detail = dict(\
    prototype='processing.hillshading',
    sources='elev_1km',
    zfactor=bathymetry_zfactor/2.,
    scale=1,
    altitude=65,
    azimuth=azimuth,
)

bathymetry_specular = dict(\
    prototype='processing.hillshading',
    sources='elev_1km',
    zfactor=bathymetry_zfactor,
    scale=1,
    altitude=85,
    azimuth=azimuth,
    )

watermask = dict(\
    prototype='datasource.mapnik',
    theme=os.path.join(themedir, 'watermask.xml'),
    image_type='png',
    buffer_size=0,
    scale_factor=1
    )

bathymetry = dict(\
    prototype='composite.imagemagick',
    sources=['bathymetry_diffuse', 'bathymetry_detail', 'bathymetry_specular', 'colorrelief', 'watermask'],
    format='png',
    command='''
    (
         ( $1 -fill grey50 -colorize 100% )
         ( $1 ) -compose blend -define compose:args=30% -composite
         ( $2 -fill #4C78FF -tint 85 -gamma 0.8  ) -compose blend -define compose:args=40% -composite
         ( $3 -gamma 3 ) -compose blend -define compose:args=30% -composite
         -brightness-contrast -10%x-5%
         ( $4 ) -compose overlay -composite
         $5 -compose copyopacity -composite
    )
    '''
    )

# ============================================================================
# Composing

composer = dict(
    prototype='composite.imagemagick',
    sources=['diffuse', 'detail', 'specular', 'landcover', 'waterbody', 'roads', 'labels', 
             'bathymetry'
            ],
    format='jpg',
    command='''
    (
         #### Relief ####
         ( $1 -fill grey50 -colorize 100% )
         ( $1 ) -compose blend -define compose:args=30% -composite
         ( $2 -fill #003cff -tint 65 -gamma 0.8  ) -compose blend -define compose:args=40% -composite
         ( $3 -gamma 2 -fill #ffd4a6 -tint 120 ) -compose blend -define compose:args=30% -composite
         -brightness-contrast -12%x-5%
         ( $4 -brightness-contrast -15%x-7% -modulate 100,100,97 ) -compose Overlay -composite
         -gamma 0.9
         -sigmoidal-contrast 2.6
         -sharpen 0x0.75

         #### Waterbodies ####         
         ( $5 ) -compose Over -composite
         #### Bathymetry ####                  
         ( $8 ) -compose Over -composite
         
         #### Road ####         
         ( $6 ) -compose Over -composite
         
         #### Label ####
         (
           $7 -geometry +0+1
           -channel A -blur 4 -evaluate Multiply 0.3 +channel
           -channel RGB -evaluate Set 0 +channel
         ) -compose Multiply -composite
         ( $7 ) -compose Over -composite
         -quality 90
    )
    '''
    )


ROOT = dict(\
    renderer='composer',
    metadata=dict(tag=tag,
                  version='1.0',
                  description='Shaded Relief Map with Natural Earth Landcover',
                  attribution='Open Street Map, SRTM Plus, SRTM30, NED 1/3", NED 1/9"',
                  ),
   cache=dict(prototype='cluster',
              stride=16,
              servers=['localhost:11211',],
              root=os.path.join(cachedir_export, 'export', '%s' % tag),
             ),

    pyramid=dict(levels=range(2, 16),
#                 envelope=[-127,27,-67,50], # US mainland
#                 envelope=[-170,16,-154,29], # US Hawaii
                 zoom=7,
                 center=(-122.1897, 46.2024),
                 format=fmt,
                 buffer=8,
                 tile_size=tile_size,
                 ),
)

