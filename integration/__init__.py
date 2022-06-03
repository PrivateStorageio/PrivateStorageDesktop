"""
Integration tests for components of the Private Storage service.

Tests here exercise an integration through::

  GridSync internals -> Tahoe-LAFS client node -> ZKAPAuthorizer -> PaymentServer
  GridSync internals -> magic-folder -> Tahoe-LAFS client -> ZKAPAuthorizer client -> ZKAPAuthorizer server -> Tahoe-LAFS storage server

That is, they integrate *almost* "end to end" with the main missing piece
being the GridSync GUI on the client end.

"""
