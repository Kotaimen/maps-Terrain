import os


zfactor = 8
azimuth = 345 
datadir = '/Users/Kotaimen/proj/geodata'
themedir= './themes/Terrain'
cachedir= os.path.join(themedir, 'cache')
tag = 'Terrain'
tile_size = 256
fmt = 'jpg'

elev_1km = dict(\
    prototype='datasource.dataset',
    dataset_path=os.path.join(datadir, 'srtm30_new/world_tiled.tif'),
    cache=dict(prototype='metacache',
        root=os.path.join(cachedir, 'elevation'),
        compress=True,
        data_format='gtiff',
        ),
    )

elev_30m = dict(\
    prototype='datasource.dataset',
    dataset_path=os.path.join(datadir, 'SRTM_30_org/world/fill/world.vrt'),
    cache=dict(prototype='metacache',
        root=os.path.join(cachedir, 'elevation'),
        compress=True,
        data_format='gtiff',
        ),
    )

elev_3m = dict(\
    prototype='datasource.dataset',
    dataset_path=os.path.join(datadir, 'st-helens/st-helens.vrt'),
    cache=dict(prototype='metacache',
        root=os.path.join(cachedir, 'elevation'),
        compress=True,
        data_format='gtiff',
        ),
    )


elev_10m = dict(\
    prototype='datasource.dataset',
    dataset_path=os.path.join(datadir, 'DEM-Tools-patch/source/ned10m/world.vrt'),    
    cache=dict(prototype='metacache',
        root=os.path.join(cachedir, 'elevation'),
        compress=True,
        data_format='gtiff',
        ),
    )
   
   
elevation = dict(\
    prototype='composite.selector',
    sources = ['elev_1km', 'elev_30m', 'elev_10m', 'elev_3m'],
    
    #            0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18
    condition = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3],
    )

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
    zfactor=1.5,
    scale=1,
    altitude=55,
    azimuth=azimuth,
)

specular = dict(\
    prototype='processing.hillshading',
    sources='elevation',
    zfactor=zfactor,
    scale=1,
    altitude=90,
    azimuth=azimuth,
    )

colorrelief = dict(\
    prototype='processing.colorrelief',
    cache=None,
    sources='elevation',
    color_context=os.path.join(themedir, 'hypsometric-map-ocean.txt'),
    )


landcover = dict(\
    prototype='datasource.dataset',
    dataset_path=os.path.join(datadir, 'natural-earth-2.0b3/raster/NE2_HR_LC_2/NE2_HR_LC.tif'),    
    )
 
color = dict(\
    prototype='composite.selector',
    sources = ['colorrelief', 'landcover'], 
    
    #            0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18
    condition = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    )


waterbody = dict(\
    prototype='datasource.mapnik',
    theme=os.path.join(themedir, 'waterbody.xml'),
    image_type='png',
    buffer_size=0,
    scale_factor=tile_size//256
    )


composer = dict(\
    prototype='composite.imagemagick',
    sources=['diffuse', 'detail', 'specular', 'color', 'waterbody'],
    cache=dict(prototype='metacache',
              root=os.path.join(cachedir, '%s' % tag),
              data_format=fmt,
             ),
    
    format='jpg',
    command='''   
    (
        ( $1 -fill grey40 -colorize 100% )
        ( $1 ) -compose blend -define compose:args=60% -composite
        ( $2 -contrast +25% ) -compose blend -define compose:args=20% -composite    
        ( $3 -gamma 2 ) -compose blend -define compose:args=30% -composite     
        -brightness-contrast -10%x-10%
#        -gamma 0.9
        ( $4 -brightness-contrast -17%x-10% ) -compose Overlay -composite
         -sigmoidal-contrast 1
        ( $5 ) -compose Over -composite
        -sharpen 0.5
        -quality 90
    )
    '''
    )


ROOT = dict(\
    renderer='composer',
    metadata=dict(tag=tag,
                  version='1.0',
                  description='Shaded Relief Map of Mt St.Halen',
                  attribution='Open Street Map, SRTM Plus, SRTM30, NED 1/3 Arc Second, NED 1/9 Arc Second',
                  ),
    cache=dict(prototype='filesystem',
              root=os.path.join(cachedir, 'export', '%s' % tag),
              data_format=fmt,
              simple=True
             ),
    pyramid=dict(levels=range(5, 17),
#                   envelope=[-180, 20, -30, 60],        
#                    envelope=[-124, 45, -121, 47],    
                 envelope=[-122.363, 46.123, -122.02, 46.257],
                 zoom=7,
                 center=(-122.1897, 46.2024),
                 format=fmt,
                 buffer=4,
                 tile_size=tile_size,
                 ),
)
