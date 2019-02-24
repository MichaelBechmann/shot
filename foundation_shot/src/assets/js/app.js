import $ from 'jquery';
import 'what-input';

// Foundation JS relies on a global varaible. In ES6, all imports are hoisted
// to the top of the file so if we used`import` to import Foundation,
// it would execute earlier than we have assigned the global variable.
// This is why we have to use CommonJS require() here since it doesn't
// have the hoisting behavior.
window.jQuery = $;
require('foundation-sites');

// If you want to pick and choose which modules to include, comment out the above and uncomment
// the line below
//import './lib/foundation-explicit-pieces';

//import {framework_fixes} from './fixes.js'

import { Triggers } from '../../../node_modules/foundation-sites/js/foundation.util.triggers';
import { Sticky } from "foundation-sites/js/foundation.sticky";

/**
 * The framework doesn't initialize the event listeners until the document is complete.
 * Effect: The side menu doesn't open until all images are loaded.
 * https://github.com/zurb/foundation-sites/pull/10877
 * This bug should be fixed with milestone 6.6.0.
 * This fix is placed here to be executed as early as possible. Within the $(document).ready(function(){...} clause
 * it had the effect that it worked only for long loading pages! It didn't work for pages without pictures (onload($window)
 * only short time after onload($document)).
 */

Triggers.Initializers.addSimpleListeners();
Triggers.Initializers.addGlobalListeners();
$.triggersInitialized = true;
//Foundation.IHearYou = Triggers.Initializers.addGlobalListeners

$(document).foundation();

$(document).ready(function(){


    // Add information to some elements to facilitate the correct positioning depending
    // on a variable number of elements
    var classname = 'quick-menu-items-' + $('#quick-menu .button').length.toString();
    $('#content-wrapper, .top-bar').addClass(classname);

     // Add and remove a class to the off-canvas elements (side menu)
     // if the size of the title bar changes.
     // With the class the off-canvas elements can be shifted up and down accordingly.
     $('.top-bar').on('sticky.zf.stuckto:top', function(){
         var h_window  = window.innerHeight;
         var h_content = $('.off-canvas-content').height();
         if(h_content > 1.2*h_window){
             /* This condition checks whether or not the page is long enough for the top bar to be minified.
              * This is necessary to avoid toggling when the page is just fits on the display when the top bar is minified
              * but cannot be displayed completely with the extended top bar.
              */
             $('.top-bar').addClass('can-minify');
             $('.off-canvas').addClass('title-bar-slim');
             $('.title-bar-big').removeClass('title-bar-big');
         }
     }).on('sticky.zf.unstuckfrom:top', function(){
         $('.off-canvas').addClass('title-bar-big');
         $('.top-bar').removeClass('can-minify');
         $('.title-bar-slim').removeClass('title-bar-slim');
     });

     /**
      * The sticky plugin is normally initialized when the page is completely loaded including all images.
      * Here the plugin is applied programmatically (intended way: simply use attribute data-sticky in the top bar).
      * This is done to use the code in foundation_shot/node_modules/foundation-sites/js/foundation.sticky.js
      * instead of any code in /dist.
      * The code in foundation.sticky.js is modified such that the plugin is initialized when the document is ready.
      */
     var options = {marginTop:0, marginBottom: 0};
     let MyStickyTopBar = new Sticky($('#MyStickyTopBar'), options);
     MyStickyTopBar._setTransitionTrigger();

     /**
      * Toggle activity of menu item if some other item is clicked
      */
     $('#menu li:not(.is-accordion-submenu-parent):not(.active) > a').click(function(){
         $('.active').removeClass('active');
         $(this).parent().addClass('active');
     });
     $('#quick-menu a.button:not(.active)').click(function(){
         $('.active').removeClass('active');
         $(this).addClass('active');
     });

     /**
      * Close the side menu if active link is clicked
      */
     $('#menu li:not(.is-accordion-submenu-parent).active > a').click(function(){
         $('#menu').foundation('close');
     });

     /**
      * Toggle activity class when sub menu item is clicked.
      */
     $('#menu .is-accordion-submenu-parent > a').click(function(){
         $(this).parent().toggleClass('is-active');
     });



});

