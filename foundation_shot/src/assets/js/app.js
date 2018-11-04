import $ from 'jquery';
import whatInput from 'what-input';

window.$ = $;

import Foundation from 'foundation-sites';
// If you want to pick and choose which modules to include, comment out the above and uncomment
// the line below
//import './lib/foundation-explicit-pieces';


import {framework_fixes} from './fixes.js'


$(document).ready(function(){

    // Add information to some elements to facilitate the correct positioning depending
    // on a variable number of elements
    var classname = 'quick-menu-items-' + $('#quick-menu .button').length.toString();
    $('#content-wrapper').addClass(classname);


    // Invoke the function foundation() when the document is ready, i.e. the DOM is complete. Any sub-sources (e.g., images)
    // need not to be loaded yet.
    $(document).foundation();


     // Add and remove a class to the off-canvas elements (menu, schedule)
     // if the size of the title bar changes.
     // With the class the off-canvas elements can be shifted up and down accordingly.
     $('.top-bar').on('sticky.zf.stuckto:top', function(){
       $('.off-canvas, #top-bar-wrapper').addClass('title-bar-slim');
     }).on('sticky.zf.unstuckfrom:top', function(){
       $('.title-bar-slim').removeClass('title-bar-slim');

     });

     // execute fixes
     framework_fixes();

});
