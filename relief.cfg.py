#
# Extreme High Quality Shaded Relief
#

import copy

# Vertical scale
zfactor=4
# Light direction
azimuth=315

dem1 = dict(\
    name='dem',
    prototype='datasource.storage',
    storage_type='metacache',
    stride=1,
    root='./themes/Terrain/cache/elevation',
    )
    
dem1 = dict(\
    name='elevation',
    prototype='datasource.dataset',
    dataset_path='/Users/Kotaimen/proj/geodata/DEM-Tools-patch/source/ned10m/ned10m.vrt',
    cache=dict(prototype='metacache',
               root='./themes/hills/cache/elevation',
               compress=True,
               data_format='gtiff',
               ),
)

# XXX: Current config parser only supports a node tree
dem2 = copy.deepcopy(dem1)
dem3 = copy.deepcopy(dem1)
dem4 = copy.deepcopy(dem1)
landcover =  dict(\
    name='vegetation',
    prototype='datasource.dataset',
    dataset_path='/Users/Kotaimen/proj/geodata/landcover/landcover-rgb-4326.tif',
    cache=dict(prototype='metacache',
               root='./themes/hills/Terrain/landcover',
               compress=True,
               data_format='gtiff',
               ),
)



diffuse = dict(\
    name='diffuse',
    prototype='processing.hillshading',
    cache=None,
    sources=(dem1,),
    zfactor=zfactor,
    scale=1,
    altitude=30,
    azimuth=azimuth,
    )
    
detail = dict(\
    name='detail',
    prototype='processing.hillshading',
    cache=None,
    sources=(dem2,),
    zfactor=1.5,
    scale=1,
    altitude=45,
    azimuth=azimuth,
)

specular = dict(\
    name='specular',
    prototype='processing.hillshading',
    cache=None,
    sources=(dem3,),
    zfactor=zfactor,
    scale=1,
    altitude=86,
    azimuth=azimuth,
    )

color = dict(\
    name='color',
    prototype='processing.colorrelief',
    cache=None,
    sources=(dem4,),
    color_context='themes/Terrain/hypsometric-map-ocean.txt',
    )

waterbody = dict(\
    name='waterbody',
    prototype='datasource.mapnik',
    cache=None,
    theme=r'themes/Terrain/waterbody.xml',
    image_type='png',
    buffer_size=0,
    scale_factor=1,
    force_reload=True,
    )

composer = dict(\
     name='imagemagick_composer',
     prototype='composite.imagemagick',
     cache=dict(prototype='metacache',
               root='./themes/Terrain/cache/hills_vegetation',
               data_format='jpg',
               ),

     sources=[diffuse, detail, specular, color, waterbody, landcover],
     format='jpg',
     command=''' 

        ( $1 -fill grey50 -colorize 100% )
         #### Grayscale relief ####
         # "diffuse" is major light, "detail" enhances shadow detail, "specular" is
         # top highlight. 
         
        ( $1 ) -compose blend -define compose:args=25% -composite
        ( $2 -brightness-contrast +0%x+40% ) -compose blend -define compose:args=20% -composite    
        ( $3 -gamma 3 ) -compose blend -define compose:args=45% -composite     
         
         #### Note following blend is calibrated to 50% grey at flat areas.
#         -brightness-contrast -10%x+0%
#         -gamma 0.62
         -brightness-contrast -10%x+0%
         -gamma 0.75
#         
#         #### Color Relief ####
         ( $6 -modulate 95,95,105 ) -compose overlay -composite
                
        #### Select a sharpen method! ####
        #   -unsharp 2x1+0.5
         -adaptive-sharpen 2	
        #    -sharpen 0.33
        
        $5 -compose over -composite
        
        #### Final tuning ###
#         -brightness-contrast -3%x+3%
#         -modulate 100,102
        
        #### JPEG compression ####
        -quality 85
        ''',
     )


ROOT = dict(\
    metadata=dict(tag='world'),
    pyramid=dict(levels=range(7, 16),
                 format='jpg',
                 buffer=16,
                 envelope=(-113, -36, -111, 37),
                 zoom=11,
                 center=(-112, 36),
                 ),
    cache=dict(prototype='filesystem',
               root='./themes/Terrain/cache/export_vegetation',
               data_format='jpg',
               ),
    renderer=composer,
    )
