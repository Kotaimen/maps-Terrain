import os


zfactor = 4 #14 8 6 4
azimuth = 325 
datadir = '/Users/Kotaimen/proj/geodata'
themedir= './themes/Terrain'
cachedir_export= os.path.join(themedir, 'cache')
tag = 'Terrain'
tile_size = 256
fmt = 'jpg'

cachedir=os.path.join('/tmp', tag, 'cache')

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
    dataset_path=os.path.join(datadir, 'DEM-Tools-patch/source/ned100m/world_3857.tif'),
    keep_cache=False,    
    cache=dict(prototype='metacache',
        root=os.path.join(cachedir, 'elevation'),
        compress=False,
        data_format='gtiff',
        ),
    )
    
elev_30m = dict(\
    prototype='datasource.dataset',
#    dataset_path=os.path.join(datadir, '/home/pset/proj/geodata/SRTM_30_org/world/fill/world_3857.vrt'),
    dataset_path=os.path.join(datadir, '/data/tilestorage/geodata/world_srtm30.tif'),
    keep_cache=False,    
    cache=dict(prototype='metacache',
        root=os.path.join(cachedir, 'elevation'),
        compress=False,
        data_format='gtiff',
        ),
    resample_method='bilinear'
    )

elev_10m = dict(\
    prototype='datasource.dataset',
    dataset_path=os.path.join(datadir, '/data/tilestorage/geodata/world_3857.tif'),    
    keep_cache=False,    
    cache=dict(prototype='metacache',
        root=os.path.join(cachedir, 'elevation'),
        compress=False,
        data_format='gtiff',
        ),
    )
   
elev_3m = dict(\
    prototype='datasource.dataset',
    dataset_path=os.path.join(datadir, 'st-helens/st-helens.vrt'),
    keep_cache=False,    
    cache=dict(prototype='metacache',
        root=os.path.join(cachedir, 'elevation'),
        compress=False,
        data_format='gtiff',
        ),
    )

elevation = dict(\
    prototype='composite.selector',
    sources = ['elev_1km', 'elev_100m', 'elev_10m', 'elev_3m'],   
    #            0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18
    condition = [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 3, 3, 3],
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

waterbody = dict(\
    prototype='datasource.mapnik',
    theme=os.path.join(themedir, 'waterbody.xml'),
    image_type='png',
    buffer_size=0,
    scale_factor=tile_size//256
    )

roads_labels = dict(\
    prototype='datasource.mapnik',
    theme=os.path.join(themedir, 'Terrain_road-labels.xml'),
    image_type='png',
    buffer_size=256,
    scale_factor=tile_size//256
    )

composer = dict(\
    prototype='composite.imagemagick',
    sources=['diffuse', 'detail', 'specular', 'landcover', 'waterbody', 'roads_labels'], 
    format='jpg',
    command='''   
    (
         ( $1 -fill grey50 -colorize 100% )
         ( $1 ) -compose blend -define compose:args=30% -composite
         ( $2 -fill #003cff -tint 65 -gamma 0.8  ) -compose blend -define compose:args=40% -composite
         ( $3 -gamma 2 -fill #ffd4a6 -tint 120 ) -compose blend -define compose:args=30% -composite
         -brightness-contrast -12%x-5%         
         ( $4 -brightness-contrast -15%x-7% -modulate 100,100,97 ) -compose Overlay -composite
          -gamma 0.9
         ( $5 ) -compose Over -composite
         -sigmoidal-contrast 2.5
         -sharpen 0x0.75
         ( $6 ) -compose Over -composite
         -quality 89
    )
    '''
    )


ROOT = dict(\
    renderer='composer',
    metadata=dict(tag=tag,
                  version='1.0',
                  description='Shaded Relief Map',
                  attribution='Open Street Map, SRTM Plus, SRTM30, NED 1/3", NED 1/9"',
                  ),
    cache=dict(prototype='cluster',
               stride=16,
               servers=['localhost:11211',],
               root=os.path.join(cachedir_export, 'export', '%s' % tag),
              ),

    pyramid=dict(levels=range(4, 16),
                 envelope=[-124,34,-70,48],            
#                  envelope=[-125,34,-105,48.5],        
                 zoom=7,
                 center=(-122.1897, 46.2024),
                 format=fmt,
                 buffer=4,
                 tile_size=tile_size,
                 ),
)
