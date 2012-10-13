#
# Standard hill shading and gtiff tiles
#

# Default elevation, use PostGIS2 as data source
elevation = dict(\
    name='elevation',
    prototype='datasource.dataset',
    dataset_path='/home/pset/proj/data/DEM-Tools-patch/source/ned10m/ned10m.vrt',
    cache=dict(prototype='metacache',
               root='./themes/hills/cache/elevation',
               compress=True,
               data_format='gtiff',
               ),
)

# Simple relief for visualizing
relief = dict(\
    name='relief',
    prototype='processing.hillshading',
    sources=(elevation,),
    zfactor=3,
    scale=1,
    altitude=25,
    azimuth=315,
    )

composer=dict(\
    name='composer',
    prototype='composite.imagemagick',
    cache=None,
    sources=[relief,],
    format='jpg',
    command='''
    $1
    -brightness-contrast +10%x-33% -gamma 1.2
    '''
    )

ROOT = dict(\
    renderer=composer,
    metadata=dict(tag='hills'),
    pyramid=dict(levels=range(12,20),
                 envelope=(-124,35,-112,39),
                 zoom=14,
                 center=(-112, 36),
                 format='jpg',
                 buffer=16,
                 ),
)
