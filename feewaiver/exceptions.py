from rest_framework.exceptions import APIException,PermissionDenied


class FeeWaiverNotAuthorized(PermissionDenied):
    default_detail = 'You are not authorised to work on this Fee Waiver'
    default_code = 'feewaiver_not_authorized'


class InvalidStatusTransitionError(Exception):
    """Custom exception raised for invalid status transitions."""
    pass

