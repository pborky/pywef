# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="pborky"
__date__ ="$Mar 8, 2010 5:59:03 AM$"

import http_exc

class NotInitializedProperly(http_exc.HTTPInternalServerError):
    pass

class InitializationError(http_exc.HTTPInternalServerError):
    pass