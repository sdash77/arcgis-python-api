var config = require("./common");
var configureCdn = require("./configure-cdn");

//This section is a workaround for notebooks.esri.com, since it uses tmpnb
var strnb = location.href.lastIndexOf("/notebooks");
var nbextensionPath = "";
if ((strnb > 0) && (location.href.match(/.*notebooks.*esri.*com.*/))) {
    nbextensionPath = location.href.substring(0, strnb) + "/nbextensions/arcgis/";
} else {
    nbextensionPath = "/nbextensions/arcgis/";
}
//end section
config.JupyterTarget = "notebook"; 
config.BaseRequireJSConfig = {
    map : {
        "*" : {
            "arcgis-map-ipywidget": nbextensionPath + "arcgis-map-ipywidget.js",
            "legacy-mapview": nbextensionPath + "legacy-mapview.js"
        },
    },
    config : {
            has: {
              "esri-featurelayer-webgl": 1
            },

            geotext: {

            useXhr: function(url) {
                // Allow cross domain XHR requests:
                // We will route them through a proxy in onXhr below.
                // https://github.com/requirejs/text/blob/master/text.js#L129

                return true;
            },

            // In IE 9, text plugin fails even before onXhr is called:
            // It fails right when calling xhr.open:
            // https://github.com/requirejs/text/blob/master/text.js#L267
            // - This is different from other browsers which appear to fail
            // much later, allowing us a chance to append proxy below.
            // -- Probably because IE 9 does not support CORS as opposed to
            // other modern browsers that have CORS support.

            // ESRI modification: let's take over xhr.open below
            openXhr: false,

            onXhr: function(xhr, url) {
                // Route cross domain XHR through a proxy if required
                var hasCors = (
                typeof XMLHttpRequest !== "undefined"
                && ("withCredentials" in (new XMLHttpRequest()))
                );

                xhr.open(
                "GET",
                hasCors ? url : (proxyUrl + "?" + url),
                true
                );
            }
        }
    }
};
configureCdn(config, config.CdnUrl);

module.exports = config;
