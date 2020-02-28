var CdnUrl = "//js.arcgis.com/4.14/";

var CdnMainCssUrl = "https:" + CdnUrl + "esri/css/main.css";

var EsriLoaderOptions = {
    url: CdnUrl,
    dojoConfig: {
        has: {
            "esri-featurelayer-webgl": 1
        }
    }
}

var minJSAPIVersion = "4.14";

var config = {
    CdnUrl,
    CdnMainCssUrl,
    EsriLoaderOptions,
    minJSAPIVersion
};

module.exports = config;
