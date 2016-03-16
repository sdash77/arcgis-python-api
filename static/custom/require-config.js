(function() {
  
    var esriCDN =  configParameters.esriCDN;
    var proxyUrl = configParameters.proxyUrl;
  
    require.config({
    
      // Define path mappings for modules
      paths: {
        
        // [1] Modules hosted on Esri CDN.
        
        "dojo":         esriCDN + "dojo",
        "dojox":        esriCDN + "dojox",
        "dijit":        esriCDN + "dijit",
        "esri":         esriCDN + "esri",
        "dgrid":        esriCDN + "dgrid",
        "xstyle":       esriCDN + "xstyle",
        "put-selector": esriCDN + "put-selector",
        
        // [2] Modules hosted locally.
        // "location" is specified as path relative to web server root.
        
        "requirejs":  "/research/js/requirejs",
        "text":       "/research/js/requirejs/text"
      },
      
      // Use RequireJS text plugin instead of dojo/text plugin.
      // Any module that requires dojo/text plugin will use RequireJS
      // text plugin instead.
      // http://requirejs.org/docs/api.html#config
      map: {
        "*": {
          "dojo/text": "text"
        }
      },
    
      // Enable cross-domain access to Esri widget templates.
      // https://github.com/requirejs/text#custom-xhr-hooks
      // This will probably be unnecssary once we have a build solution.
      /*
      config: {
        text: {
          
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
      } */
    });
  
})();