import $ from 'jquery';
import whatInput from 'what-input';

window.$ = $;

import Foundation from 'foundation-sites';
// If you want to pick and choose which modules to include, comment out the above and uncomment
// the line below
//import './lib/foundation-explicit-pieces';


$(document).foundation();



// Add and remove a class to the off-canvas elements (menu, schedule)
// if the size of the title bar changes.
// With the class the off-canvas elements can be shifted up and down accordingly.
$('.title-bar').on('sticky.zf.stuckto:top', function(){
  $('.off-canvas').removeClass('movedown');
}).on('sticky.zf.unstuckfrom:top', function(){
  $('.off-canvas').addClass('movedown');
})
