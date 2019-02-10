/**
 * This file contains fixes of the java script framework which turned out to be necessary to make Foundation 6.5.0 work
 * as expected.
 */

import { Triggers } from '../../../node_modules/foundation-sites/js/foundation.util.triggers';
import $ from 'jquery';
function framework_fixes(){

    /**
     * The framework doesn't initialize the event listeners until the document is complete.
     * Effect: The side menu doesn't open until all images are loaded.
     * https://github.com/zurb/foundation-sites/pull/10877
     */
    Triggers.Initializers.addSimpleListeners();
    Triggers.Initializers.addGlobalListeners();

    /**
     * The line below initializes the sticky plugin. Without this line it doesn't work correctly
     * until all images are completely loaded.
     * Effect: The top bar doesn't adjust when scrolling to and from the top!
     * see: https://github.com/zurb/foundation-sites/issues/10505
     */
    $(window).trigger("load.zf.sticky");
}

export {framework_fixes}