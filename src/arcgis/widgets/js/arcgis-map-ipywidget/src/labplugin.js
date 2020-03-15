var arcgisMapIPyWidget = require('./arcgis-map-ipywidget/arcgis-map-ipywidget.js');
var base = require('@jupyter-widgets/base');
var version = require('../package.json').version;
var PhosphorWidgets = require("@phosphor/widgets");
var images = require('./arcgis-map-ipywidget/images/images');

class IPythonExtensionWidgetContainer extends PhosphorWidgets.Widget{
    constructor(element, title) {
        super();
        this.ipywidgetElement = element;
        this.originalParentElement = element.parentElement
        this.originalParentElement.removeChild(element);
        this.node.appendChild(element);
        this.id = "ipywidget-external-window-container-" + Math.random().toString(36).substring(7);
        this.title.label = title;
        this.title.closable = true;
        this.addClass('IPythonExtensionWidgetContainer');
    }

    restoreToOriginalParentElement(msg){
        this.originalParentElement.appendChild(this.ipywidgetElement);
        while(this.node.hasChildNodes()){
            this.node.removeChild(widget.node.lastChild);
            }
        //TODO: find more elegant solution to this ugly hack
        this.mapForAllChildrenOfIPyWidgetElement((childNode) => {
            if(childNode.id && /.*new.*window/i.test(childNode.id)){
                ///For the icon that was previously hidden, redisplay it
                childNode.src = images.toNewWindowEncoded;
                this.ipywidgetElement.style.height = this.ipywidgetElement.prevElementHeight;
                }
        });
    }

    mapForAllChildrenOfIPyWidgetElement(func){
        var recursiveChildDescend = function(node){
            for(var i=0; i < node.childElementCount; i++){
                var child = node.childNodes[i];
                recursiveChildDescend(child);
                func(child);
            }
        };
        recursiveChildDescend(this.ipywidgetElement);
    }
};

module.exports = {
    id: 'arcgis-map-ipywidget',
    requires: [base.IJupyterWidgetRegistry],
    activate: function(app, widgets) {
        widgets.registerWidget({
            name: 'arcgis-map-ipywidget',
            version: version,
            exports: arcgisMapIPyWidget
        });
        window.newJLabWindow = function(args){
            ///TODO: Find more elegant, less global way to do this
            console.log("Attempting to create new window with these args:");
            console.log(args);
            var ipyExtWinCon = new IPythonExtensionWidgetContainer(args.element, args.title);
            if(args.tab_mode === "auto"){
                autoPlaceInMainArea(app, ipyExtWinCon);
            }
            else{
                app.shell.add(ipyExtWinCon, "main", {mode: args.tab_mode});
            }
            // Activate the widget
            app.shell.activateById(ipyExtWinCon.id);
        };
        window.closeJLabWindow = function(args){
            console.log("Attempting to close window with these args:");
            console.log(args);
            var phosphorWidgets = getAllPhosphorWidgets();
                   for(var j in phosphorWidgets){
                        var pwidget = phosphorWidgets[j];
                        if(pwidget.node != null){
                            for(var k in pwidget.node.children){
                                var child = pwidget.node.children[k];
                                if(child.id == args.element.id){
                                    pwidget.restoreToOriginalParentElement();
                                    pwidget.close();
                                    break;
                                }
                            }
                        }
                   }
         };
        var autoPlaceInMainArea = function(app, ipyExtWinCon){
            //TODO: make this logic more elegant and robust
            try{
                var numPhosphorWidgetsInMain = 0;
                var widgets = app.shell.widgets("main");
                while (widget = widgets.next()){
                       numPhosphorWidgetsInMain++;
                    }
                var numWidgetsInCurrentTab = app.shell._currentTabBar().titles.length;
                var numActiveWindows = numPhosphorWidgetsInMain - numWidgetsInCurrentTab + 1;
                console.log("Attempting to autoplace widget among " + numActiveWindows + 
                    " other active widgets.");
                if(numActiveWindows <= 1){
                    app.shell.add(ipyExtWinCon, "main", {mode: "split-right"});
               } else {
                    app.shell.add(ipyExtWinCon, "main", {mode: "tab-after"});
                }
            } catch(err) {
                console.log("Unhandled error while 'auto' mode of placing tabs" + 
                    ". Just adding this widget in 'tab-after' mode");
                console.log(err);
                app.shell.add(ipyExtWinCon, "main", {mode: "tab-after"});
            }
        };
        var getAllPhosphorWidgets = function(){
            var outputWidgets = []
            var areas = ['main', 'left', 'right', 'top', 'bottom'];
            for(var i in areas){
                var area = areas[i];
                try{
                    var widgets = app.shell.widgets(area);
                    while (widget = widgets.next()){
                        outputWidgets.push(widget);
                    }
                } catch(err) {
                   //ignore errors, since not all jlab instances have all of
                    //left, right, top, bottom, etc.
                }
            }
            return outputWidgets
        }
      },
  autoStart: true
};
