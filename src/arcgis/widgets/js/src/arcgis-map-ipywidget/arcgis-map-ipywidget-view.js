//The main module that exports the javascript widget class

//import all external modules
const widgets = require('@jupyter-widgets/base');
const _ = require('lodash');

//import all helper functions
var createElements = require('./elements/create-elements');
var displayPureJSErrorBox = require('./elements/display-purejs-error-box');
var loadingProgressDisplay = require('./elements/loading-progress-display');
var inferNoTypeLayer = require('./layer-utils/infer-no-type-layer');
var icons = require('./icons/icons');
var mainCssString = require('../css/main.css').toString();
var chromeSafariCssString = require('../css/chrome-safari-workaround.css').toString();
var configureCDN = require("../config/configure-cdn");

//import the configuration and the specific esri-loader based off the config
var config = require("config")
var getEsriLoader = require('./loaders/get-esri-loader');
var esriLoader = getEsriLoader(config);
var options = config.EsriLoaderOptions;

console.log("Using this config:");
console.log(config);

//Apply the mainCssString defined in ../css/main.css
var _applyCssString = function(cssString){
    var style = document.createElement("style");
    style.innerHTML = cssString;
    document.head.appendChild(style);
}
_applyCssString(mainCssString);

//Apply the ArcGIS JS API's main.css to the document
var _applyCssFromUrl = function(url){
    var link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = url
    document.head.appendChild(link);
}
_applyCssFromUrl(config.CdnMainCssUrl);

//The arbitrary layer ID for all custom drawn graphics
const graphicsLayerId = "graphicsLayerId31195";

var ArcGISMapIPyWidgetView = widgets.DOMWidgetView.extend({

    render: function() {
    ///This is called once the first time the widget is drawn in the notebook
    this._override_right_click_menu();
    this._apply_css_workaround();
    this._setup_js_cdn();
    this._setup_elements();
    this.model.set("jupyter_target", config.JupyterTarget);
    loadingProgressDisplay.start();
    esriLoader.loadModules(['esri/Map',
                            'esri/views/MapView',
                            'esri/views/SceneView',
                            'esri/core/watchUtils'], options).then((
                            [Map,
                             MapView,
                             SceneView,
                             watchUtils]) => {
        loadingProgressDisplay.stop();
        this._setup_custom_buttons();
        this._instantiate_esri_components(Map, MapView, SceneView);
        this._setup_stationary_callback(watchUtils);
        this._miscellanous_setup();

        //All model specific change functions. These functions are called
        //whenever that attribute on the model is updated, whether that update
        //comes from Python, from the UI, etc. The callback function is called on change
        //start map specific draw state
        this.model.on('change:mode', this.mode_changed, this);
        this.model.on('change:basemap', this.basemap_changed, this);
        this.model.on('change:zoom', this.zoom_changed, this);
        this.model.on('change:rotation', this.rotation_changed, this);
        this.model.on('change:heading', this.heading_changed, this);
        this.model.on('change:tilt', this.tilt_changed, this);
        this.model.on('change:_extent', this.extent_changed, this);
        this.model.on('change:_center', this.center_changed, this);
        this.model.on('change:_center_long_lat', this.center_long_lat_changed, this);
        //start layer specific model types
        this.model.on('change:_func_chains', this.func_chains_changed, this);
        this.model.on('change:_add_this_notype_layer', this.add_this_notype_layer_changed, this);
        this.model.on('change:_layers_to_remove', this.layers_to_remove_changed, this);
        this.model.on('change:_add_this_graphic', this.graphics_changed, this);
        //end layer specific model types
        //start webmap/websceme section
        this.model.on('change:_webmap', this.webmap_changed, this);
        this.model.on('change:_webscene', this.webscene_changed, this);
        this.model.on('change:_trigger_webscene_save_to_this_portal_id', this.save_webscene, this);
        //end webmap/webscene section
        //start miscellanous model section
        this.model.on('change:_portal_token', this.portal_token_changed, this);
        this.model.on('change:_custom_msg', this.custom_msg_changed, this);
        this.model.on('change:hide_mode_switch', this.hide_mode_switch_changed, this);
        this.model.on('change:_trigger_interactive_draw_mode_for', this.interactive_draw_shape, this);
        this.model.on('change:_trigger_new_jlab_window_with_args', this.trigger_jlab_window_changed, this);
        this.model.on('change:_fallback_cdn_changed', this.fallback_cdn_changed, this);
        //end miscellanous model section

        //Last thing to do: update the widget state from the model's
        this.update_widget_from_model().then(() => {
            this._postLoadSetup();
        });
    }).catch((err) => {
       this._displayErrorBox();
       console.warn("Error on render: "); console.warn(err);
        });
    },

    update_widget_from_model: function(){
        return new Promise((resolve, reject) => {
            //start map specific draw state
            this.mode_changed();
            this.basemap_changed();
            this.zoom_changed();
            this.rotation_changed();
            this.heading_changed();
            this.tilt_changed();
            this.center_long_lat_changed();
            this.center_changed();
            this.extent_changed();
            //end map specific draw state
            //start miscellanous model section
            this.hide_mode_switch_changed();
            this.portal_token_changed();
            this.authenticate_to_portal().then((_) => {
                //Authenticate to the portal before attempting to load anything
                //end miscellanous model section
                //start layer specific model calls
                this.draw_these_notype_layers_on_widget_load();
                this.draw_these_graphics_on_widget_load();
                //end layer specific model calls
                //start webmap/webscene section
                this.webmap_changed();
                this.webscene_changed();
                //end webmap/webscene section
                resolve();
            }).catch((err) => {
                this._displayErrorBox("Error while authenticating to portal on first load.");
                console.warn("Error during portal auth"); console.warn(err);
                reject(err);
            });
        })
    },

    _displayErrorBox: function(msg, browser_console_message = true){
        ///A simple message box display mechanism
        if (!msg){
            msg = "Unhandled Error! See the browser console for more info.";
        }
        else if (browser_console_message) {
            msg += " See the browser console for more info.";
        }
        loadingProgressDisplay.stop();
        if (!document.getElementById(this.elements.errorTextBox.id)){
            //If everything has failed to load, add the error box so it displays
            this.el.appendChild(this.elements.errorTextBox);
        }
        if(!this.elements.errorTextBox.textContent){
            //If there's no current message box open
            displayPureJSErrorBox(msg, this.elements); 
        } else {
            //There's another message still open: save all messages
            //to browser console and alert user
            var multiple_messages_info = "Multiple messages attempted to " + 
                "display. See browser console to view all messages";
            if(this.elements.errorTextBox.textContent !== multiple_messages_info){
                console.warn("*****MESSAGE_BOX: " +
                    this.elements.errorTextBox.textContent);
            }
            console.warn("*****MESSAGE_BOX: " + msg);
            displayPureJSErrorBox(multiple_messages_info, this.elements);
        }
    },

    _apply_css_workaround: function(){
        ///In jupyter notebook (not lab), there's a special CSS override
        ///needed for chrome and safari for certain layer types to load
        if((config.JupyterTarget === "notebook") &&
              ((navigator.userAgent.indexOf("Chrome") != -1) ||
               (navigator.userAgent.indexOf("Safari") != -1))){
            _applyCssString(chromeSafariCssString);
        }
    },

    _setup_elements: function(){
        this.uuid = Math.random().toString(36).substring(7);
        this.elements = createElements(this.uuid);
        this.el.className = "arcgisMapIPyWidgetDiv";
        this.el.style.height = "100%";
        this.el.style.width = "100%";
        this.el.appendChild(this.elements.viewdivElement);
    },

    _setup_custom_buttons: function(){
        ///Now that we're loaded, add the 2D/3D switch, new window button, etc
        //2D/3D switch setup
        this.elements.infodivElement.appendChild(this.elements.switchButton);
        this.elements.switchButton.onclick = () => {
            if(this.model.get("mode") === "3D"){
                this.model.set("mode", "2D");
                this.touch();
            } else {
                this.model.set("mode", "3D");
                this.touch();
            }
        }
        //jupyterlab new window button setup
        if(config.JupyterTarget === "lab"){
            this.elements.infodivElement.appendChild(this.elements.newWindowButton);
            this.elements.newWindowButton.onclick = () => {
                this.move_to_new_jlab_window({title: "ArcGIS Map"});
            }
        }
    },

    _setup_stationary_callback: function(watchUtils){
        //The moment the mouse enters the arcgis js api 2d/3d view (not parent element),
        //Set up responses to the 'stationary' callback (i.e., what logic to run
        //when the user clicks the map, zooms, changes extent, etc.). Only set this up once
        this._2dMap._pointerMoveHandler = this._2dMap.on(
            ['pointer-move', 'key-down'], (event) => {
                console.log("Started interacting with the 2D map, " + 
                    "setting up stationary callback...");
                watchUtils.when(this._2dMap, "stationary", this._2dStationaryCallback)
                this._2dMap._pointerMoveHandler.remove();
        });
        this._3dMap._pointerMoveHandler = this._3dMap.on(
            ['pointer-move', 'key-down'], (event) => {
                console.log("Started interacting with the 3D map, " + 
                    "setting up stationary callback...");
                watchUtils.when(this._3dMap, "stationary", this._3dStationaryCallback)
                this._3dMap._pointerMoveHandler.remove();
        });
    },

    _2dStationaryCallback: function(){
        ///Do 2D specific stationary callbacks before common stuff
        var widget_inst = this._parentIPyWidget;

        var rotation = this.rotation;
        if(rotation >= 0){
            widget_inst.model.set("rotation", rotation);
        }

        widget_inst._commonStationaryCallback(widget_inst);
    },

    _3dStationaryCallback: function(){
        ///Do 3D specific stationary callbacks before common stuff
        var widget_inst = this._parentIPyWidget;

        var camera = this.camera;
        if(camera){
            widget_inst.model.set("heading", camera.heading);
            widget_inst.model.set("tilt", camera.tilt);
        }

        widget_inst._commonStationaryCallback(widget_inst);
    },

    _commonStationaryCallback: function(widget_inst){
        ///This function is a callback for the 'stationary' event on the activeView
        ///('stationary' is when the map stops moving on a zoom, a pan, etc.)
        ///Since it is a callback, 'this' is actually the instance of either the
        ///the 2d MapView or 3D SceneView
        var zoom = widget_inst.activeView.zoom;
        if(zoom >= 0){
            //this callback is sometimes errenously called, displaying nonexistant values
            widget_inst.model.set("zoom", zoom);
        }

        var center = widget_inst.activeView.center;
        if(center){
            widget_inst.model.set("_readonly_center", JSON.parse(JSON.stringify(center)))
        }

        var extent = widget_inst.activeView.extent;
        if(extent){
            widget_inst.model.set("_readonly_extent", JSON.parse(JSON.stringify(extent)));
        }
        widget_inst.model.save_changes();
    },

    _miscellanous_setup: function(){
       ///Every time the 2d map changes a basemap/ground/layer, call this function
        this._2dMap.map.allLayers.on('change', (event) => {
            this.update_readonly_webmap();
        });
        this._3dMap.map.allLayers.on('change', (event) => {
            this.update_readonly_webmap();
        });
    },

    _postLoadSetup: function(){
        //Whenever either the 2d or 3d view loads, set model var 'ready' to
        //true for python to consume
        console.log("Calling postLoad");
        this._2dMap.when(() => {
            console.log("2D map ready");
            this.model.set('ready', true)
            this.model.set('_readonly_extent', this._2dMap.extent);
            this.model.set('_readonly_center', this._2dMap.center);
            this.model.save_changes();
        });

        this._3dMap.when(() => {
            console.log("3D map ready");
            this.model.set('ready', true)
            this.model.set('_readonly_extent', this._3dMap.extent);
            this.model.set('_readonly_center', this._3dMap.center);
            this.model.save_changes();
        });

        //Whenever you click on the map, send an event for python to listen to
        this._2dMap.on(['click'], (event_) => {
            this.send({ event: 'mouseclick', message: event_.mapPoint });
        });

        this._3dMap.on(['click'], (event_) => {
            this.send({ event: 'mouseclick', message: event_.mapPoint });
        });

    },

    _setup_js_cdn: function(){
        //set up any CDN override before we call esri modules
        this.model.on('change:_js_cdn_override', this.js_cdn_changed, this);
        this.js_cdn_changed();
    },

    _instantiate_esri_components: function(Map, MapView, SceneView){
        this.map = new Map({ground: "world-elevation"});
        this.container = this.elements.mapElement;
        this._3dMap = new SceneView({map: this.map, container: this.container});
        this._3dMap._parentIPyWidget = this;
        this._2dMap = new MapView({map: this.map, container: this.container});
        this._2dMap._parentIPyWidget = this;
        this.activeView = this._2dMap;
    },


    _override_right_click_menu: function(){
        this.el.addEventListener('contextmenu', function(e) {
            //alert("You tried to open a context menu");
            e.preventDefault();
            e.stopPropagation();
            return false;
        }, false);
    },

    custom_msg_changed: function(){
        var _custom_msg = this.model.get("_custom_msg");
        if(_custom_msg){
            this._displayErrorBox(_custom_msg,
                                  browser_console_message = false);
        }
    },

    basemap_changed: function () {
        try{
            console.log("updating basemap...");
            this.map.basemap = this.model.get('basemap');
        } catch(err){
            this._displayErrorBox();
            console.warn("Error on basemap_change: "); console.warn(err)
        }
        //TODO: REMOVE ME!
        console.log("Widget = ");
        console.log(this);
    },

    mode_changed: function(){
    try{
        console.log("updating mode...");
        this.activeView.container = null;
        if(this.model.get("mode") === "3D"){
            this.elements.switchButton.src = icons.sceneToMapEncoded;
            if(this.activeView.viewpoint){
                this._3dMap.viewpoint = this.activeView.viewpoint.clone();
            }
            this._3dMap.container = this.container;
            this.activeView = this._3dMap;
            this._3dMap.map = this.map
            this._2dMap.map = null;
        } else {
            this.elements.switchButton.src = icons.mapToSceneEncoded;
            if(this.activeView.viewpoint){
                this._2dMap.viewpoint = this.activeView.viewpoint.clone();
             }
             this._2dMap.container = this.container;
             this.activeView = this._2dMap;
             this._2dMap.map = this.map;
             this._3dMap.map = null;
             //Set the 'tilt' to 0 whenever switching to 2D mode
             this.model.set("tilt", 0);
             this.model.save_changes();
        }
    } catch(err){
        this._displayErrorBox();
        console.warn("Error on mode_changed"); console.warn(err); 
    }
    },

    zoom_changed: function(){
        try{
            var zoom = this.model.get("zoom")
            this.activeView.zoom = zoom;
        } catch(err){
            this._displayErrorBox("Error while modifying zoom.");
            console.warn("Error on zoom"); console.warn(err);
        }
    },

    rotation_changed: function(){
        try{
            var rotation = this.model.get("rotation");
            this._2dMap.rotation = rotation
        } catch(err){
            this._displayErrorBox("Error while modifying rotation");
            console.warn("Error on rotation"); console.warn(err);
        }
    },

    heading_changed: function(){
        ///TODO: Find more elegant way to implement this func and tilt_changed()
        var _applyHeading = function(this_) {
            //The actual function that is eventually called to apply the heading
            var heading = this_.model.get("heading");
            var camera = this_._3dMap.camera.clone();
            camera.heading = heading;
            this_._3dMap.camera = camera
        };
        esriLoader.loadModules(["esri/core/watchUtils"],
        options).then(([watchUtils]) => {
            if(this._3dMap.camera){
                //If the map is already initialized
                _applyHeading(this);
            } else{
                //set up the callback when the camera is ready for consumption
                watchUtils.once(this._3dMap, "camera", () => {
                    _applyHeading(this);
               })
            }
        }).catch((err) =>{
            this._displayErrorBox("Error while modifying heading");
            console.warn("Error on heading"); console.warn(err);
        });
    },

    tilt_changed: function(){
        var _applyTilt = function(this_){
            //The actual function that is eventually called to apply the tilt
            this_._3dMap.goTo({center: this_._3dMap.center,
                              tilt: this_.model.get("tilt")});
        };
        esriLoader.loadModules(["esri/core/watchUtils"],
        options).then(([watchUtils]) => {
            if(this._3dMap.camera){
                //If the map is already initialized
                _applyTilt(this);
           } else {
                //Set up the callback when the camera is ready for consuption
                watchUtils.once(this._3dMap, "camera", () => {
                    _applyTilt(this);
                });
            }
        }).catch((err) =>{
            //TODO: Figure out why the 'h is null' error happens, fix it
            //For now, don't display an error box, just log to console
            //this._displayErrorBox("Error while modifying tilt");
            console.warn("Error on tilt"); console.warn(err);
        });
    },

    extent_changed: function(){
        esriLoader.loadModules(['esri/geometry/Extent'],
        options).then(([Extent]) => {
            var extent = this.model.get("_extent");
            if(extent.xmin){
                //Prevents an error about a bad extent
                this.activeView.extent = new Extent(extent);
            }
        }).catch((err) => {
            this._displayErrorBox("Error while modifying extent.");
            console.warn("Error on extent"); console.warn(err);
        });
    },

    center_long_lat_changed: function(){
        ///When the center is passed in as a [long,lat] list, add it to the view
        ///Then watch the view until it changes center into the correct format,
        ///which we will then update correctly via the _center model attribute
        esriLoader.loadModules(["esri/core/watchUtils"],
        options).then(([watchUtils]) => {
            var _center_long_lat = this.model.get("_center_long_lat");
            if(_center_long_lat.length === 2){
                console.log("Converting [long, lat] center to standard center...");
                //Set up the callback when the view's center is ready for consuption
                watchUtils.once(this.activeView, "center", () => {
                    console.log("Center is converted");
                    var view_center = JSON.parse(JSON.stringify(this.activeView.center));
                    this.model.set("_center", view_center);
                    this.model.set("_center_long_lat", []);
                    this.model.save_changes();
                })
                //Actually update the center on the activeView to trigger the above
                this.activeView.center = _center_long_lat
            }
       }).catch((err) =>{
            this._displayErrorBox("Error while modifying center_long_lat.");
            console.warn("Error on center_long_lat"); console.warn(err);
        });
 
    },

    center_changed: function(){
        ///this function is called when _center is in the correct format
        try{
            var _center = this.model.get("_center");
            if('x' in _center && 'y' in _center){
                this.activeView.center = _center;
            }
        }catch(err){
            this._displayErrorBox("Error while modifying center");
            console.warn("Error on center"); console.warn(err);
        }
    },

    webmap_changed: function(){
    esriLoader.loadModules(['esri/WebMap']).then(([WebMap]) => {
        console.log("Updating webmap...");
        var webmap_from_python = this.model.get("_webmap");
        if(Object.keys(webmap_from_python).length !== 0){
            this.authenticate_to_portal().then((portal) => {
                webmap_from_python.portalItem.portal = portal;
                var webmap = new WebMap(webmap_from_python);
                webmap.load().then((webmap) => {
                    this._2dMap.map = webmap;
                    this.map = webmap;
                    this.update_readonly_webmap();
                }).catch((err) => {
                    this._displayErrorBox("Error on loading webmap item");
                    console.warn("Error on loading webmap"); console.warn(err);
                });
            }).catch((err) => {
                this._displayErrorBox("Error on loading portal for webmap");
                console.warn("Error on loading webmap"); console.warn(err);
            });
        }
    }).catch((err) => {
        this._displayErrorBox("Error on loading webmap from portal");
        console.warn("Error on loading webmap"); console.warn(err);
    });
    },

    update_readonly_webmap: function() {
        ///Whenever a layer/basemap/ground is changed, OR whenever the webmap
        ///is directly changed, update an esri JSON representation of the webmap
        ///for readonly consumption on the python side of things
        try{
            var map;
            if(this._2dMap.map){
                map = this._2dMap.map}
            else {
                map = this._3dMap.map
            }
            var layers_json = []
            for(var i in map.layers.toArray()){
                //TODO: Implement WebMap.toJSON() when it's added to JS API
                var layer = map.layers.toArray()[i]
                var layer_json = { id : layer.id,
                                   normalization : layer.normalization,
                                   refreshInterval : layer.refreshInterval,
                                   url : layer.url };
                if (layer.graphics){
                    layer_json.graphics = [];
                    for(var i in layer.graphics.toArray()){
                        var graphic = layer.graphics.toArray()[i];
                        var graphic_json = graphic.toJSON();
                        graphic_json.shape = graphic.shape;
                        layer_json.graphics.push(graphic_json);
                    }
                }
                if (layer.renderer){
                    layer_json.renderer = layer.renderer.toJSON();
                    layer_json.rendererType = layer.renderer.declaredClass;}
                layers_json.push(layer_json) }
            var wm = { layers : layers_json,
                       ground : map.ground.toJSON(),
                       basemap : map.basemap.toJSON() };
            this.model.set('_readonly_webmap_from_js', wm);
            this.model.save_changes();
        } catch(err){
            this._displayErrorBox("Error updating readonly webmap json.");
            console.warn("Error updatin readonly webmap"); console.warn(err); }
    },

    webscene_changed: function(){
        esriLoader.loadModules(['esri/WebScene',
                                'esri/Viewpoint',
                                'esri/webscene/InitialViewProperties']).then(
        ([WebScene, ViewPoint, InitialViewProperties]) => {
        console.log("Updating webscene...");
        console.log(this.model.get("_webscene"))
        var webscene_from_python = this.model.get("_webscene");
        if(Object.keys(webscene_from_python).length !== 0){
            this.authenticate_to_portal().then((portal) => {
                webscene_from_python.portalItem.portal = portal;
                var webscene = new WebScene(webscene_from_python);
                webscene.load().then((webscene) => {
                    this._3dMap.map = webscene;
                    this.map = webscene;
                }).catch((err) => {
                    this._displayErrorBox("Error on loading webscene item");
                    console.warn("Error on loading webscene"); console.warn(err);
                });
            }).catch((err) => {
                this._displayErrorBox("Error on loading portal for webscene");
                console.warn("Error loading portal"); console.warn(err);
                
            });
        }
    }).catch((err) => {
        this._displayErrorBox("Error on loading webscene from portal");
        console.warn("Error on loading webscene"); console.warn(err);
    });
 
    },

    save_webscene: function(){
        esriLoader.loadModules(['esri/WebScene',
                                'esri/Ground',
                                'esri/Basemap']).then(
        ([WebScene,
          Ground,
          Basemap]) => {
            this.authenticate_to_portal().then((portal) => {
                var scene;
                if(this._3dMap.map.declaredClass == "WebScene"){
                    scene = new WebScene(this._3dMap.map.toJSON())}
                else{
                    scene = new WebScene({layers : this._3dMap.map.layers,
                        ground : Ground.fromJSON(this._3dMap.map.ground.toJSON()),
                        basemap : Basemap.fromJSON(this._3dMap.map.basemap.toJSON())});}
                var portal_item_id = this.model.get("_trigger_webscene_save_to_this_portal_id");
                console.log("Starting to save webscene to portal item " + portal_item_id); 
                scene.portalItem = {
                        id: portal_item_id,
                        portal: portal};
                scene.load().then(() => {
                    scene.ground = Ground.fromJSON(this._3dMap.map.ground.toJSON());
                    scene.basemap = Basemap.fromJSON(this._3dMap.map.basemap.toJSON());
                    scene.updateFrom(this._3dMap);
                    scene.save({ignoreUnsupported: true}).then((item) => {
                        console.log("The following item was saved:");
                        console.log(item.toJSON());
                   }).catch((err) => {
                        this._displayErrorBox("Error saving webscene");
                        console.warn("Error saving webscene"); console.warn(err);
                    });
                    //TODO: clean up, figure out why layers are deleted on save
                    this.reload_all_layers();
                    this._3dMap.map = scene;
                    this.map = scene;

                }).catch((err) => {
                    this._displayErrorBox("During load, error on loading webscene save");
                    console.warn("Error loading web scene"); console.warn(err);
                })
            }).catch((err) => {
                this._displayErrorBox("During portal auth, error on webscene save");
                console.warn("Error portal auth on webscene save"); console.warn(err);});
        }).catch((err) => {
            this._displayErrorBox("Error on saving the web scene");
            console.warn("Error saving web scene"); console.warn(err);
        });
    },

    reload_all_layers: function(){
        console.log("TODO: CHECK IF I'M BROKEN");
        this.draw_these_notype_layers_on_widget_load();
    },

    func_chains_changed: function(){
            console.log("Updating func_chains...");
            console.log(this.model.get("_func_chains"));
    },

    draw_these_notype_layers_on_widget_load: function(){
        var layers = this.model.get('_draw_these_notype_layers_on_widget_load');
        console.log("Drawing these layers on load... ");
        console.log(layers);
        for(var i in layers){
            var noTypeLayer = layers[i];
            this.add_notype_layer(noTypeLayer);
        }
    },

    add_this_notype_layer_changed: function(){
        var noTypeLayer = this.model.get("_add_this_notype_layer");
        if(Object.keys(noTypeLayer).length !== 0){
            this.add_notype_layer(noTypeLayer);
       }
   },

    add_notype_layer: function(noTypeLayer){
       inferNoTypeLayer(noTypeLayer, this).then((typedLayer) => {
            var layerExistsOnMap = Boolean(this.map.findLayerById(
                typedLayer.id));
            console.log("Adding Layer " + noTypeLayer._hashFromPython + " " +
                "to map.");
            this.map.add(typedLayer);
        }).catch((err) => {
            this._displayErrorBox("Could not update layer. " + err);
            console.warn("Could not update layer"); console.warn(err);
            });
    },

    layers_to_remove_changed: function(){
        try{
            console.log("Called layer to remove changed...");
            var _layers_to_remove = this.model.get("_layers_to_remove");
            for(var i in _layers_to_remove){
                var layerId = _layers_to_remove[i];
                do {
                    var layer = this.map.findLayerById(layerId);
                    var layerExistsOnMap = Boolean(layer);
                    if(layerExistsOnMap){
                        console.log("Attempting to remove layer" + layer.id);
                        this.map.remove(layer);
                    }
                } while(layerExistsOnMap);
            }
        } catch(err){
            this._displayErrorBox("Error removing layer");
            console.warn("Error removing layer"); console.warn(err);
        }
    },

    hide_mode_switch_changed: function(){
        //NOTE: it is only possible to remove this element
        //To 'recreate', you must instantiate a whole new object
        if(this.model.get("hide_mode_switch")){
            console.log("Removing the mode switch...");
            this.elements.switchButton.remove();
        }
    },

    getGraphicsLayer: function(GraphicsLayer){
        ///All graphics are drawn on 1 layer: return it if it's been made,
        ///Make it if it hasn't
        var graphicsLayer = this.map.findLayerById(graphicsLayerId);
        if(typeof graphicsLayer === "undefined"){
            graphicsLayer = new GraphicsLayer({
                id: graphicsLayerId});
            this.map.add(graphicsLayer);
        }
        return graphicsLayer
    },

    draw_these_graphics_on_widget_load: function(){
        var graphics = this.model.get('_draw_these_graphics_on_widget_load');
        console.log("Drawing these layers on load... ");
        console.log(graphics);
        for(var i in graphics){
            var graphic_json = graphics[i];
            this.add_graphic(graphic_json);
        }
    },

    graphics_changed: function(){
        var graphic_json = this.model.get("_add_this_graphic");
        if(Object.keys(graphic_json).length !== 0){
            this.add_graphic(graphic_json);
       }
    },

    add_graphic: function(graphic_json){
        esriLoader.loadModules(['esri/layers/GraphicsLayer',
                                'esri/Graphic',
                                'esri/geometry/Geometry',
                                'esri/symbols/Symbol'],
        options).then(([GraphicsLayer,
                        Graphic,
                        Geometry,
                        Symbol]) => {
            var gfx = new Graphic(graphic_json);
            if(gfx.symbol == null) {
                console.log(gfx.geometry);
                if (/polyline/i.test(gfx.geometry.type)) {
                    gfx.symbol = { type: 'simple-line' }
                } else if (/polygon/i.test(gfx.geometry.type)) {
                    gfx.symbol = { type: "simple-fill" };
                } else if (/point/i.test(gfx.geometry.type)) {
                    gfx.symbol = { type: 'simple-marker' }
                } else if (/multipoint/i.test(gfx.geometry.type)) {
                    gfx.symbol = { type: 'simple-marker' }
                }
        }
        var graphicsLayer = this.getGraphicsLayer(GraphicsLayer);
        graphicsLayer.add(gfx);
        }).catch((err) => {
            this._displayErrorBox("Error on updating graphics.");
            console.warn("Error on updating graphics"); console.warn(err);
        });
    },

    interactive_draw_shape: function(){
        esriLoader.loadModules(['esri/widgets/Sketch/SketchViewModel',
                                'esri/layers/GraphicsLayer',
                                'esri/Graphic'],
        options).then(([SketchViewModel,
                        GraphicsLayer,
                        Graphic]) => {
            console.log("Entering interactive draw shape mode.");
            var shape = this.model.get("_trigger_interactive_draw_mode_for");
            if(shape){
                var view = this.activeView;
                var graphicsLayer = this.getGraphicsLayer(GraphicsLayer);
                var sketch = new SketchViewModel({
                  view: view,
                });
                sketch.create(shape);
                sketch.on("create-complete", (event) => {
                    var graphic = new Graphic({
                        geometry: event.geometry,
                        symbol: sketch.graphic.symbol});
                    graphic.shape = shape;
                    graphicsLayer.add(graphic)
                    this.update_readonly_webmap();
                    console.log("Sending draw-end event...");
                    this.send({ event: 'draw-end', message: graphic.geometry.toJSON() })
                });
            }
        }).catch((err) => {
            this._displayErrorBox("Error on drawing interactive shape");
            console.warn("Error on interactive shape"); console.warn(err);
        });
   },

    trigger_jlab_window_changed: function(){
        var args = this.model.get("_trigger_new_jlab_window_with_args");
        console.log("new_jlab_window triggered with:");
        console.log(args);
        if(Object.keys(args).length !== 0){
            this.move_to_new_jlab_window(args)
        }
    },

    move_to_new_jlab_window: function(args){
        if(config.JupyterTarget !== "lab"){
            this._displayErrorBox("Can only move to new window in a " + 
                                  "JupyterLab env");
            console.warn("Can't move to new window: JupyterTarget = " + 
                          config.JupyterTarget);
            return
        }
        console.log("Attempting to move map to new jlab window...");
        var childMapElement = this.el.childNodes[0];
        console.log(childMapElement);
        if(childMapElement != null){
            //Element is currently in the notebook; so, move it to a new window
            var window_title = args.title;
            var tab_mode;
            if ("tab_mode" in args){
                tab_mode = args.tab_mode
            } else {
                tab_mode = this.model.get("tab_mode"); }
            window.newJLabWindow({title: window_title,
                                  element: childMapElement,
                                  tab_mode: tab_mode});
            //hide the icon when you're in seperate window mode
            this.elements.newWindowButton.src = icons.toOriginalWindowEncoded;
            //Store the previous height of the element
            this.prevElementHeight = this.el.style.height;
            this.el.style.height = "0px";
        } else {
            //element is currently in a new window (or is somewhere else)
            //So, move it back to the notebook
            var activeMapElement = document.getElementById(
                this.elements.viewdivElement.id);
            window.closeJLabWindow({element: activeMapElement});
            this.elements.newWindowButton.src = icons.toNewWindowEncoded;
            this.el.style.height = this.prevElementHeight;
        }
    },

    portal_token_changed: function(){
    try{
        var _portal_token = this.model.get("_portal_token");
        if(_portal_token){
            console.log("updating _portal_token...");
            this._portalToken = _portal_token
            this.model.set("_portal_token", "");
            this.model.save_changes();
        }
    } catch (err) {
        this._displayErrorBox("Error storing token.");
        console.warn("Error storing token."); console.warn(err);
    }
    },

    authenticate_to_portal: function(){
        ///Given all relevant information in the model, attempt to authenticate
        ///to the portal, then return the portal. Then, resolve the portal obj
        ///On any error, reject the Promise
        ///The _portal_token should be deleted and set to this before this
        ///function is called if you're planning on using auth
    return new Promise((resolve, reject) => {
        esriLoader.loadModules(['esri/config',
                                'esri/identity/ServerInfo',
                                'esri/identity/IdentityManager',
                                'esri/portal/Portal'],
        options).then(([esriConfig,
                        ServerInfo,
                        IdentityManager,
                        Portal]) => {
            var _auth_mode = this.model.get("_auth_mode");
            if(('_portal' in this) && (this._portal.loaded)){
                //If we've previously set up a portal & its loaded, resolve it
                resolve(this._portal);
            } else if(_auth_mode.toLowerCase() === "anonymous"){
                //If we specified an anonymous connection, load it and resolve
                var _portal_url = this.model.get("_portal_url");
                if(_portal_url !== ""){
                    esriConfig.portalUrl = _portal_url;
                }
                this._portal = new Portal({authMode: 'anonymous'});
                this._portal.load().then(() => {
                    resolve(this._portal);
                }).catch((err) => {
                    reject(err);
                });
            } else if (_auth_mode.toLowerCase() === "tokenbased"){
                //If we specified token based authentication, attempt to resolve it
                var _portal_url = this.model.get("_portal_url");
                var _portal_sharing_rest_url = this.model.get("_portal_sharing_rest_url");
                if(!(_portal_url && _portal_sharing_rest_url && this._portalToken)){
                    reject("_portal_url, _portal_sharing_rest_url, and _portal_token " + 
                           "must be specified to authenticate in 'tokenBased' auth mode");
                } else {
                    var serverInfo = new ServerInfo();
                    serverInfo.server = _portal_sharing_rest_url;
                    serverInfo.tokenServiceUrl = _portal_sharing_rest_url + 'generateToken';
                    IdentityManager.registerServers([serverInfo]);
                    IdentityManager.registerToken({"server": _portal_sharing_rest_url,
                                                  "userId": this.model.get("_username"),
                                                  "token": this._portalToken});
                    this._portal = new Portal({
                        url: _portal_url});
                    this._portal.load().then(() => {
                        resolve(this._portal);
                    }).catch((err) => {
                        reject(err);
                    });
                }
            } else if (_auth_mode.toLowerCase() === "prompt"){
                var _portal_url = this.model.get("_portal_url");
                if(_portal_url !== ""){
                    esriConfig.portalUrl = _portal_url;
                }
                this._portal = new Portal({
                    authMode: 'immediate',
                    allSSL: false,
                    canSignInArcGIS: true,
                    canSignInIDP: true,
                    authorizedCrossOriginDomains: [esriConfig.portalUrl,]});
                this._portal.load().then(() => {
                    resolve(this._portal);
                }).catch((err) => {
                    reject(err);
                });
             } else {
                reject("You must specify the '_auth_mode' model variable to " + 
                       "either 'anonymous', 'tokenbased', or 'prompt'");
            }
        }).catch((err) => {
                reject(err);
            });
    })},

    js_cdn_changed: function() {
        var fallback_cdn = this.model.get("_js_cdn_override");
        if(fallback_cdn !== ""){
            configureCDN(config, fallback_cdn);
            console.log("CDN changed: new config = ");
            console.log(config);
            options = config.EsriLoaderOptions;
            this._check_js_api_version_loaded(fallback_cdn);
            css_url = fallback_cdn + "esri/css/main.css"
            if(config.JupyterTarget === "notebook"){
                esriLoader.setRequireJSConfig(config.BaseRequireJSConfig);
                //TODO: remove this jquery for notebook css adding
                $('head').append($('<link rel="stylesheet" type="text/css" />'
                    ).attr('href', css_url));
            } else if(config.JupyterTarget === "lab"){
                esriLoader.loadCss(css_url)
            }
            esriLoader.loadModules(['esri/config'],
            options).then(([esriConfig,]) => {
                esriConfig.request.corsEnabledServers.push(fallback_cdn)
            }).catch((err) => {
                console.log("Error while setting fallback cdn");
                console.log(err);
            });
        }
    },

    _check_js_api_version_loaded: function(fallback_cdn){
        this._httpGetAsync(fallback_cdn).then((response) => {
            //TODO: find better parsing logic for finding out what version
            var lines = response.split("\n");
            var copyrightLine = null; //copyright.txt line link contains version #
            for(var i = 0; i < lines.length; i++){
                var line = lines[i];
                if((line.indexOf("js.arcgis.com") !== -1) && 
                   (line.indexOf("copyright.txt") !== -1)){
                    copyrightLine = line;
                    break;
                }
            }
            if(copyrightLine !== null){
                console.log("Copyright line = '" + copyrightLine + "'");
                var versionNum = copyrightLine.split(
                    "js.arcgis.com/")[1].split("/esri")[0];
                if (versionNum < config.minJSAPIVersion){
                    console.warn("JS API " + versionNum + " < " + config.minJSAPIVersion);
                    this._displayErrorBox("Warning: the ArcGIS API for JavaScript " + 
                        "being loaded at " + fallback_cdn + " does not appear to be " +
                        ">=" + config.minJSAPIVersion + ". Widget may not function " + 
                        "properly.", browser_console_message=false);
                }
            } else {
                console.warn("Could not infer javascript version");
                this._displayErrorBox("Warning: Could not infer version of any " +
                    "loaded ArcGIS API for JavaScript. Widget may not function " +
                    "properly.", browser_console_message=false);
            }
        }).catch((err) => {
            console.log("Could not reach the fallback cdn...");
            console.log(err);
        });
    },

    _httpGetAsync : function(theUrl){
        return new Promise((resolve, reject) => {
            fetch(theUrl, {mode: 'cors'}).then((response) => {
                if (response.status >= 200 && response.status < 300){
                    response.text().then((data) => {
                        resolve(data);
                    }).catch((err) => {
                        reject(err);
                    });
                } else {
                    reject("HTTP request on " + theUrl + 
                           " returned code " + status);
                }
            })
        })
    },
});

module.exports = ArcGISMapIPyWidgetView;

